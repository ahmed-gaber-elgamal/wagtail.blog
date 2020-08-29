from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock

class TitleAndTextBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text='Add your title')
    text = blocks.TextBlock(required=True, help_text='Add your text')
    class Meta:
        # template = "streams/title_and_text_block.html"
        icon = "edit"
        label = "Title and Text"


class RichtextBlock(blocks.RichTextBlock):
    class Meta:
        icon = "edit"
        label = "Full Richtext"

class CardBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Add your title")
    cards = blocks.ListBlock(blocks.StructBlock([
        ("image", ImageChooserBlock(required=True)),
        ('title', blocks.CharBlock(required=True, max_length=50)),
        ("text", blocks.TextBlock(required=True, max_length=250)),
        ("button_page", blocks.PageChooserBlock(required=False)),
        ("button_url", blocks.URLBlock(required=False, help_text="if the button page above is selected, that will be used first"))
    ]))
    class Meta:
        template = "streams/card_block.html"
        icon = "placeholder"
        label = "owner card"