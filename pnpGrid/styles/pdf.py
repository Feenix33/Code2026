from terrain import TerrainType
from terrain_style import TerrainStyle


STYLE = {

    TerrainType.GRASS:
        TerrainStyle("white", "dots"),

    TerrainType.WATER:
        TerrainStyle("white", "waves"),

    TerrainType.FOREST:
        TerrainStyle("white", "trees"),

    TerrainType.MOUNTAIN:
        TerrainStyle("white", "rocks"),

    TerrainType.DESERT:
        TerrainStyle("white", "sand"),

    TerrainType.SWAMP:
        TerrainStyle("white", "cross"),

    TerrainType.ROAD:
        TerrainStyle("gray", "solid"),

    TerrainType.CITY:
        TerrainStyle("white", "grid"),
}
