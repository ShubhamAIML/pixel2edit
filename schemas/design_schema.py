from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class CanvasConfig(BaseModel):
    width: int = Field(default=1080, description="Canvas width in pixels")
    height: int = Field(default=1350, description="Canvas height in pixels")
    background: str = Field(default="#FFFFFF", description="Background color in hex (#RRGGBB) or CSS gradient")


class Position(BaseModel):
    x: float = Field(default=0, description="Horizontal X position in pixels from top-left")
    y: float = Field(default=0, description="Vertical Y position in pixels from top-left")


class Size(BaseModel):
    width: float = Field(default=200, description="Width in pixels")
    height: float = Field(default=60, description="Height in pixels")


class SpacingBox(BaseModel):
    top: float = Field(default=0)
    right: float = Field(default=0)
    bottom: float = Field(default=0)
    left: float = Field(default=0)


class ElementLayout(BaseModel):
    padding: SpacingBox = Field(default_factory=SpacingBox)
    margin: SpacingBox = Field(default_factory=SpacingBox)


class ElementTransform(BaseModel):
    rotation: float = Field(default=0, description="Rotation angle in degrees (-360 to 360)")


class ElementStyle(BaseModel):
    fontFamily: str = Field(default="Inter", description="Font family name")
    fontSize: float = Field(default=32, description="Font size in pixels")
    fontWeight: int = Field(default=400, description="Numeric font weight e.g. 300, 400, 600, 700, 800")
    fontStyle: Literal["normal", "italic"] = Field(default="normal")
    textDecoration: Literal["none", "underline", "line-through"] = Field(default="none")
    color: str = Field(default="#1e293b", description="Text color in hex (#RRGGBB) or rgba")
    backgroundColor: str = Field(default="transparent", description="Background color")
    borderRadius: float = Field(default=0, description="Border radius in pixels")
    borderWidth: float = Field(default=0, description="Border width in pixels")
    borderColor: str = Field(default="transparent", description="Border color")
    textAlign: Literal["left", "center", "right", "justify"] = Field(default="left")
    lineHeight: float = Field(default=1.2, description="Line height multiplier (e.g. 1.2, 1.4)")
    letterSpacing: float = Field(default=0, description="Letter spacing in pixels")
    textTransform: Literal["none", "uppercase", "lowercase", "capitalize"] = Field(default="none")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0, description="Opacity from 0.0 to 1.0")


class DesignElement(BaseModel):
    id: str = Field(..., description="Unique element identifier, e.g. text_001, btn_001")
    type: Literal["text", "heading", "paragraph", "button", "rectangle", "circle", "image", "background"] = Field(
        default="text", description="Type of visual element"
    )
    content: Optional[str] = Field(default="", description="Text content or label")
    position: Position = Field(default_factory=Position)
    size: Size = Field(default_factory=Size)
    style: ElementStyle = Field(default_factory=ElementStyle)
    layout: ElementLayout = Field(default_factory=ElementLayout)
    transform: ElementTransform = Field(default_factory=ElementTransform)
    zIndex: Optional[int] = Field(default=1, description="Stacking order")


class DesignDocument(BaseModel):
    canvas: CanvasConfig = Field(default_factory=CanvasConfig)
    elements: List[DesignElement] = Field(default_factory=list)
