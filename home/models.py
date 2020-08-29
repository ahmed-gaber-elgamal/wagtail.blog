# from django.db import models
#
# from wagtail.core.models import Page
# from wagtail.core.fields import RichTextField
# from wagtail.admin.edit_handlers import FieldPanel
#
#
# class HomePage(Page):
#     body = RichTextField(blank=True)
#
#     content_panels = Page.content_panels + [
#         FieldPanel('body', classname="full"),
#     ]
from django.db import models

from wagtail.api import APIField
from wagtail.core.models import Page, Orderable
from modelcluster.fields import ParentalKey
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel, InlinePanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailautocomplete.edit_handlers import AutocompletePanel
# from wagtail.admin.edit_handlers import
from streams import blocks
# from wagtailleafletwidget.edit_handlers import GeoPanel
# from django.utils.functional import cached_property
# from wagtailleafletwidget.helpers import geosgeometry_str_to_struct
from wagtailgeowidget.edit_handlers import GeoPanel
from django.utils.functional import cached_property
from wagtailgeowidget.helpers import geosgeometry_str_to_struct
from django.utils.translation import ugettext as _


class HomePage(Page):
    parent_page_type = ['wagtailcore.Page']
    subpage_types = [
        'blogger.BlogIndexPage',
        'contact.ContactPage',
        'home.BlogAbout'
    ]
    banner_title = models.CharField(max_length=250, blank=False, null=True)
    banner_subtitle = RichTextField(features=['bold', 'italic'])
    banner_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    banner_cta = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = RichTextField(blank=True)
    api_fields = [
        APIField('banner_title'),
        APIField('banner_image'),
        APIField('banner_cta'),
        APIField('banner_subtitle')
    ]
    content_panels = Page.content_panels + [
        FieldPanel('banner_title'),
        FieldPanel('banner_subtitle'),
        ImageChooserPanel('banner_image'),
        AutocompletePanel('banner_cta'),
        FieldPanel('body', classname='full'),
        MultiFieldPanel([
            InlinePanel("carousel_images", max_num=5, min_num=1)
        ], heading='carousel images')

    ]
    custom_panels = [
        FieldPanel('banner_title'),
        FieldPanel('banner_subtitle'),
        ImageChooserPanel('banner_image'),
    ]

    # override edit_handler
    # edit_handler = TabbedInterface([
    #     ObjectList(content_panels, heading='Content'),
    #     ObjectList(Page.promote_panels, heading='Promote'),
    #     ObjectList(Page.settings_panels, heading='Settings'),
    #     ObjectList(custom_panels, heading='Sidebar Settings')
    # ])
    def get_context(self, request):
        context = super().get_context(request)
        blog_indexes = self.get_children().live().order_by('-first_published_at')
        context['blog_indexes'] = blog_indexes
        return context


class BlogAbout(Page):
    subpage_types = []
    max_count = 1
    address = models.CharField(max_length=250, blank=True, null=True)
    location = models.CharField(max_length=250, blank=True, null=True)

    content = StreamField([
        ("title_and_text", blocks.TitleAndTextBlock()),
        ("Full_richtext", blocks.RichtextBlock()),
        ("card_block", blocks.CardBlock()),
    ], null=True,
       blank=True
    )
    subtitle = models.CharField(max_length=250, blank=True, null=True)
    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        StreamFieldPanel("content"),

        MultiFieldPanel([
            FieldPanel('address'),
            GeoPanel('location', address_field='address'),
        ], _('Geo details')),


    ]
    @cached_property
    def point(self):
        return geosgeometry_str_to_struct(self.location)

    @property
    def lat(self):
        return self.point['y']

    @property
    def lng(self):
        return self.point['x']

class HomePageCarouselImages(Orderable):
    page = ParentalKey('home.HomePage', on_delete=models.CASCADE, related_name='carousel_images')
    carousel_image = models.ForeignKey('wagtailimages.Image', on_delete=models.CASCADE, related_name='+', null=True, blank=False)
    caption = models.CharField(blank=True, max_length=250)
    panels = [
        ImageChooserPanel('carousel_image'),
        FieldPanel('caption')
    ]