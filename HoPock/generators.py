from datetime import datetime
import calendar

class CurrentMonthGenerator:
    def process(self, target_arg=None):
        now = datetime.now()
        cal_text = calendar.month(now.year, now.month)
        return f"Generated Calendar:\n{cal_text}"

class TableOfContentsGenerator:
    def process(self, target_arg=None):
        return "Generated TOC page..."

