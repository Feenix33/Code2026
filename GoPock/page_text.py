from page import Page, PageFactory
from reportlab.platypus import Frame, Paragraph, PageBreak, Spacer
from reportlab.lib import colors
import os
import processors
import logging
import sys
import inspect

from style_registry import KNOWN_PARAGRAPH_STYLES, paragraph_style_configs

logger = logging.getLogger(__name__)
dbgINFO = True # print INFO messages or not

"""
TODO
- Fix the reset command: procesor should return a reset type and text is the style to reset

operation: the processor is passing a pargraph style object, not using the ones from text page
need to get rid of the debug in the old program and adjust the spaceAfter if the font size changes
rest should be good

- if change fontsize need to change spacing too
- Potentiall add more heading styles for the markdown processor
- Add the other troff commands

"""

@PageFactory.register("text")
class TextPage(Page):
    def __init__(self, text="", title="Generic Text Page", **kwargs):
        super().__init__()
        self.text = text
        self.title = title

        # Defer file I/O and processing to draw(). Store args for later.
        self._file_arg = kwargs.get('file') or kwargs.get('filename')
        self._processor = kwargs.get('processor')
        self._path_arg = kwargs.get('path')
        self._cache_enabled = bool(kwargs.get('cache', False))
        self._last_full_path = None
        self._last_mtime = None
        self._last_processed = None

        self._paragraph_styles = None

    def _resolve_full_path(self, file_arg, path_arg):
        if not file_arg:
            return None
        file_expanded = os.path.expanduser(file_arg)
        if os.path.isabs(file_expanded):
            return file_expanded
        if path_arg:
            p = str(path_arg).lower()
            if p == 'local':
                base = os.path.dirname(__file__)
            elif p == 'global':
                base = os.getcwd()
            else:
                base = os.path.expanduser(path_arg)
                if not os.path.isabs(base):
                    base = os.path.abspath(os.path.join(os.getcwd(), base))
        else:
            base = os.path.dirname(__file__)
        return os.path.join(base, file_expanded)

    def _ensure_paragraph_styles(self):
        if self._paragraph_styles is None:
            self._build_section_styles()
        return self._paragraph_styles

    def _section_style_definitions(self, base_kwargs):
        styles = paragraph_style_configs(base_kwargs)
        return {
            style_name: self.buildParagraphStyle(**style_kwargs)
            for style_name, style_kwargs in styles.items()
        }

    def _build_section_styles(self):
        from data_classes import Font

        base_font = self.get_style("font")
        if base_font is None:
            base_font = Font()

        base_kwargs = {
            'fontName': base_font.name,
            'fontSize': base_font.size,
            'textColor': base_font.color,
        }

        self._paragraph_styles = self._section_style_definitions(base_kwargs)

    def _normalize_style_name(self, style_name):
        if style_name is None:
            return 'body'

        normalized = str(style_name).lower()
        if normalized in self._ensure_paragraph_styles():
            return normalized

        logger.warning(
            "Unknown paragraph style '%s' in paragraph; defaulting to body. Available styles: %s",
            style_name,
            ', '.join(sorted(KNOWN_PARAGRAPH_STYLES)),
        )
        return 'body'

    def _reset_style(self, style_name):
        if style_name == 'all':
            self._paragraph_styles = None
            return

        normalized = self._normalize_style_name(style_name)
        self._paragraph_styles[normalized] = self._build_style_by_name(normalized)

    def _build_style_by_name(self, style_name):
        from data_classes import Font

        base_font = self.get_style("font")
        if base_font is None:
            base_font = Font()

        base_kwargs = {
            'fontName': base_font.name,
            'fontSize': base_font.size,
            'textColor': base_font.color,
        }

        return self._section_style_definitions(base_kwargs).get(style_name, self._section_style_definitions(base_kwargs)['body'])

    def _get_paragraph_style(self, style_name, overrides=None):
        styles = self._ensure_paragraph_styles()
        base_style = styles.get(self._normalize_style_name(style_name), styles['body'])

        if not overrides:
            return base_style

        style_kwargs = {
            'fontName': base_style.fontName,
            'fontSize': base_style.fontSize,
            'textColor': base_style.textColor,
            'alignment': base_style.alignment,
            'leftIndent': base_style.leftIndent,
            'firstLineIndent': base_style.firstLineIndent,
            'bulletIndent': base_style.bulletIndent,
            'spaceBefore': base_style.spaceBefore,
            'spaceAfter': base_style.spaceAfter,
            'leading': base_style.leading,
        }
        alignment_override = overrides.get('align') or overrides.get('alignment')
        if isinstance(alignment_override, str):
            style_kwargs['align'] = alignment_override.lower()
            overrides = {k: v for k, v in overrides.items() if k not in ('align', 'alignment')}

        style_kwargs.update(overrides)
        return self.buildParagraphStyle(**style_kwargs)

    def addObject(self, obj):
        if isinstance(obj, PageBreak):
            if hasattr(self, 'book') and self.book is not None and getattr(self.book, 'addPages', False):
                self.book.insertOverflow(self)
            else:
                print("WARNING: page break encountered but addPages is disabled; stopping page rendering")
        else:
            print(f"WARNING: unsupported object type {type(obj)} passed to addObject")

    def _read_and_process(self):
        if not self._file_arg:
            if self._processor:
                proc_obj = processors.get(self._processor)
                if proc_obj:
                    use_abbrev = False
                    if hasattr(self, 'book') and self.book is not None:
                        use_abbrev = getattr(self.book.config, 'useRecipeAbbreviations', False)
                    return proc_obj.process(
                        self.text,
                        source_path=None,
                        page=self,
                        book=self.book,
                        use_abbreviations=use_abbrev,
                    )
            return self.text

        full_path = self._resolve_full_path(self._file_arg, self._path_arg)
        if not full_path:
            return f"Error: no file specified"

        try:
            mtime = os.path.getmtime(full_path)
        except Exception as e:
            logger.warning("Cannot stat file %s: %s", full_path, e)
            return f"Error: cannot access file {self._file_arg}: {e}"

        if self._cache_enabled and self._last_full_path == full_path and self._last_mtime == mtime:
            return self._last_processed

        try:
            with open(full_path, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except Exception as e:
            logger.warning("Cannot read file %s: %s", full_path, e)
            return f"Error: cannot read file {self._file_arg}: {e}"

        if self._processor:
            proc_obj = processors.get(self._processor)
            if proc_obj:
                use_abbrev = False
                if hasattr(self, 'book') and self.book is not None:
                    use_abbrev = getattr(self.book.config, 'useRecipeAbbreviations', False)
                processed = proc_obj.process(
                    content,
                    source_path=full_path,
                    page=self,
                    book=self.book,
                    use_abbreviations=use_abbrev,
                )
            else:
                processed = content
        else:
            processed = content

        if self._cache_enabled:
            self._last_full_path = full_path
            self._last_mtime = mtime
            self._last_processed = processed

        return processed

    def draw(self, canvas):
        mgn = 10
        frame = Frame(mgn, mgn, self.max.x - mgn, self.max.y - mgn, showBoundary=1)
        text_to_render = self._read_and_process()

        # Helper to attempt adding a new page when requested or on error
        def _attempt_add_page():
            if hasattr(self, 'book') and self.book is not None and getattr(self.book, 'addPages', False):
                try:
                    # original lines
                    # new_page = self.__class__(**(self.overrides or {}))
                    # self.book.add_page(new_page)
                    # cme attempt to fix the issue
                    # print("Attempting overflow insertion")
                    self.book.insertOverflow(self)
                    if dbgINFO: print(f"INFO: Added new page of type {self.__class__.__name__} due to content overflow or .np command")
                except Exception as e:
                    print(f"WARNING: failed to add new page automatically: {e}")
            else:
                # print("WARNING: content overflow or .np encountered; stopping page rendering")
                print("WARNING: content overflow on page {self.debugID} incomplete rendering")

        if isinstance(text_to_render, list):
            # dbgI = 1
            for item in text_to_render:
                # print (f"[{dbgI}] {item}")
                # dbgI += 1

                if item.get("type") == "newpage":
                    # handle explicit new page or break page command
                    if hasattr(self, 'book') and self.book is not None and getattr(self.book, 'addPages', False):
                        self.addObject(PageBreak())
                        frame = Frame(mgn, mgn, self.max.x - mgn, self.max.y - mgn, showBoundary=1)
                        continue
                    else:
                        print("WARNING: page break encountered but addPages is disabled; stopping page rendering")
                        break

                if item.get('type') == 'reset':
                    # handle reset command
                    if item.get('style') == 'all':
                        # print("DEBUG: 238 Resetting all styles to defaults")
                        self._reset_style('all')
                    # else:
                    # print(f"DEBUG: 241 Resetting style '{item.get('style')}' to defaults")
                    continue

                if item.get('type') == 'spacer':
                    style = self._get_paragraph_style(item.get('style', 'body'), item.get('style_args'))
                    # obj = Spacer(1, style.spaceAfter)
                    obj = Spacer(1, style.fontSize)  # cme adjust to font size instead of spaceAfter
                    try:
                        res = frame.add(obj, canvas)
                    except Exception as e:
                        print(f"WARNING: exception while adding spacer: {e}")
                        _attempt_add_page()
                        break
                    if res == 0:
                        _attempt_add_page()
                        frame = Frame(mgn, mgn, self.max.x - mgn, self.max.y - mgn, showBoundary=1)
                        res = frame.add(obj, canvas)
                        if res == 0:
                            print("ERROR: Spacer is too large for page")
                            sys.exit(1)
                    continue

                if item.get('type') != 'paragraph':
                    continue

                style = self._get_paragraph_style(item.get('style', 'body'), item.get('style_args'))

                # print(f"DEBUG: 248 {vars(style)}")
                # print(f"DEBUG: 248 fontSize={style.fontSize} spaceAfter={style.spaceAfter} leading={style.leading}")
                obj = Paragraph(item.get('text', ''), style)
                try:
                    res = frame.add(obj, canvas)
                except Exception as e:
                    print(
                        f"WARNING {inspect.currentframe().f_lineno}: exception while adding paragraph: {e}"
                    )
                    _attempt_add_page()
                    break

                # If frame.add returns 0, treat as overflow/error
                if res == 0:
                    # print("WARNING: frame.add returned 0 (no space) — stopping page rendering")
                    # print(f"DEBUG: {sys._getframe().f_code.co_name}({self.debugID})")
                    _attempt_add_page()
                    # now add the frame
                    frame = Frame(mgn, mgn, self.max.x - mgn, self.max.y - mgn, showBoundary=1)
                    res = frame.add(obj, canvas)
                    if res == 0:
                        print ("ERROR: Paragraph is too long for page")
                        sys.exit(1)
                    # break  # cme to correct frame addition issue
        else:
            currentStyle = self._get_paragraph_style('body')
            obj = Paragraph(text_to_render, currentStyle)
            try:
                res = frame.add(obj, canvas)
            except Exception as e:

                print(
                    f"WARNING {inspect.currentframe().f_lineno}: exception while adding paragraph: {e}"
                )
                _attempt_add_page()
                return
            if res == 0:
                print("WARNING: frame.add returned 0 (no space) — stopping page rendering")
                _attempt_add_page()
