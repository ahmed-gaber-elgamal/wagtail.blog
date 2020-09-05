from django.db import models
from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.core.fields import StreamField
from django_countries.fields import CountryField
from wagtail.contrib.routable_page.models import route, RoutablePageMixin
from django.shortcuts import render
from streams import blocks
from django_comments_xtd.models import XtdComment


class BlogIndexPage(RoutablePageMixin, Page):

    subpage_types = [
        'blogger.BlogPage',

    ]
    parent_page_types = ['home.HomePage']
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        paginator = Paginator(blogpages, 1)
        page = request.GET.get("page")
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context['blogpages'] = blogpages
        context['categories'] = BlogCategory.objects.all()
        context['posts'] = posts
        return context

    @route(r"^category/(?P<cat_slug>[-\w]*)/$", name="category_view")
    def category_view(self, request, cat_slug):
        context = self.get_context(request)
        category = BlogCategory.objects.get(slug=cat_slug)
        context['category'] = category
        context['posts'] = BlogPage.objects.filter(categories__in=[category])
        return render(request, "home/category.html", context)

    @route(r"^categories/$", name="categories_view")
    def categories_view(self, request):
        context = self.get_context(request)
        categories = BlogCategory.objects.all
        context['categories'] = categories
        # context['posts'] = BlogPage.objects.filter(categories__in=[category])
        return render(request, "home/categories.html", context)

    @route(r"^year/(\d+)/$", name="year_view")
    def year_view(self, request, year=None):
        context = self.get_context(request)
        context['year'] = year
        if year is not None:
            posts = BlogPage.objects.live().public().filter(release=year)
        else:
            posts = BlogPage.objects.live().public().filter(release=2020)
        print(year)
        context['posts'] = posts
        return render(request, "home/release.html", context)

    @route(r"^years/$", name="years_view")
    def years_view(self, request):
        context = self.get_context(request)
        # context['year'] = year
        posts = BlogPage.objects.live().public().all()
        # print(year)
        context['posts'] = posts
        return render(request, "home/releases.html", context)


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class BlogPage(RoutablePageMixin, Page):
    subpage_types = []
    parent_page_types = ['blogger.BlogIndexPage']
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField('blogger.BlogCategory', blank=True)
    release = models.IntegerField(default=2000)

    sequel = StreamField([
        ('title_and_text', blocks.TitleAndTextBlock()),

    ], null=True,
        blank=True
    )

    @route(r'^search/$', name="post_search")
    def post_search(self, request, *args, **kwargs):
        search_query = request.GET.get('q', None)
        self.posts = self.get_posts()
        if search_query:
            self.posts = self.posts.filter(body__contains=search_query)
            self.search_term = search_query
            self.search_type = 'search'
        return Page.serve(self, request, *args, **kwargs)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('release'),
            FieldPanel('tags'),
            FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
            InlinePanel('customcomments', label='Comments'),

        ], heading='Blog information'),
        FieldPanel('intro'),
        FieldPanel('body', classname='full'),
        InlinePanel('gallery_images', label='Gallery Images'),
        StreamFieldPanel("sequel"),
    ]

    def get_absolute_url(self):
        return self.get_url()

class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]
class BlogPageAuthor(Orderable):
    page = ParentalKey(BlogPage, related_name="post_author", null=True)
    author = models.ForeignKey(
        "blogger.BlogAuthor",
        on_delete=models.CASCADE,
        null=True
    )
    panels = [
        SnippetChooserPanel("author")
    ]

class BlogTagIndexPage(Page):

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context
class BlogAuthor(models.Model):
    name = models.CharField(max_length=250)
    website = models.URLField(blank=True, null=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="+"
    )
    panels =  [
        MultiFieldPanel([
            FieldPanel('name'),
            ImageChooserPanel("image"),
        ], heading='Author information'),
        MultiFieldPanel([
            FieldPanel('website'),
            ], heading='Links'),

    ]
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Post Author"
        verbose_name = "Post Authors"
register_snippet(BlogAuthor)

@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        verbose_name='slug',
        blank=True,
        allow_unicode=True,
        max_length=250,
        help_text='a slug to identify posts by this category'
    )
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog categories'


class CustomComment(XtdComment):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='customcomments')
    
    def save(self, *args, **kwargs):
        self.user_name = self.user.username
        self.page = BlogPage.objects.get(pk=self.object_pk)
        super(CustomComment, self).save(*args, **kwargs)