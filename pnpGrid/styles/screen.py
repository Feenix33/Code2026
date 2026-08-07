from terrain import TerrainType
from terrain_style import TerrainStyle

STYLE = {
    TerrainType.GRASS:
        TerrainStyle((80,180,80), "solid"),
    TerrainType.WATER:
        TerrainStyle((70,120,255), "solid"),
    TerrainType.FOREST:
        TerrainStyle((20,120,20), "solid"),
    TerrainType.MOUNTAIN:
        TerrainStyle((140,140,140), "solid"),
    TerrainType.DESERT:
        TerrainStyle((230,220,120), "solid"),
    TerrainType.SWAMP:
        TerrainStyle((80,110,50), "solid"),
    TerrainType.ROAD:
        TerrainStyle((90,90,90), "solid"),
    TerrainType.CITY:
        TerrainStyle((200,80,80), "solid"),
}
