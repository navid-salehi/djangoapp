from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.http import HttpRequest,HttpResponse, Http404
from .models import Bords, Topic, Post
from .forms import NewTopicForm, PostForm
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, View, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.urls import reverse_lazy
#---------------------------------------------------------------------
#def home(request): 
#    bordS = Bords.objects.all()
#    return render(request, 'home.html', {'bordS':bordS})

class BoardListView(ListView):
    model = Bords
    context_object_name = 'bordS'
    template_name = 'home.html'
#------------------------------------------------------------------
#@login_required
#def board_topics(request, pk):
#    bord = get_object_or_404(Bords, pk = pk)
#    topics = bord.topics.order_by('-last_update').annotate(replies=Count('posts') - 1)
#    return render(request, 'topics.html', {'bord': bord, 'topics': topics})

#def board_topics(request, pk):
#    bord = get_object_or_404(Bords, pk=pk)
#    queryset = bord.topics.order_by('-last_update').annotate(replies=Count('posts')- 1)
#    page = request.GET.get('page', 1)

#    paginator = Paginator(queryset, 5)

#    try:
#        topics = paginator.page(page)
#    except PageNotAnInteger:
        # fallback to the first page
#        topics = paginator.page(1)
#    except EmptyPage:
        #probably the user tried to add a page number
        #in the url, so we fallback to the last page
#        topics = paginator.page(paginator.num_pages)
#    return render(request, 'topics.html',{'bord': bord, 'topics':topics})

class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 5

    def get_context_data(self, **kwarg):
        kwarg['bord'] = self.bord
        return super().get_context_data(**kwarg)

    def get_queryset(self):
        self.bord = get_object_or_404(Bords, pk=self.kwargs.get('pk'))
        queryset = self.bord.topics.order_by('-last_update').annotate(replies=Count('posts') - 1)
        return queryset

#-------------------------------------------------------------------   
@login_required
def new_topic(request, pk):
    bord = get_object_or_404(Bords, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = bord
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=bord.pk, topic_pk=topic.pk) 
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html',{'bord':bord, 'form': form})

#----------------------------------------------------------------
#def topic_posts(request, pk, topic_pk):
#    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
#    topic.views += 1
#    topic.save()
#    return render(request, 'topic_posts.html', {'topic': topic})

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)    
        if not self.request.session.get(session_key, False):    
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset
#----------------------------------------------------------------
@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            topic.last_update = timezone.now()
            topic.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
            
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})
#----------------------------------------------------------------
@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect ('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


#---------------------------------------------------------------
#CBV class based view
#class NewPostView(View):
#    def render(self, request):
#        return render(request, 'new_post.html', {'form': self.form})
#
#    def post(self, request):
#        self.form = PostForm(request,POST)
#        if self.form.is_valid():
#            self.form.save()
#            return redirect('post_list')
#        return self.render(request)
    
#    def get(self, request):
#        self.form = PostForm()
#        return self.render(request)

#GCBV Generic Class Based View
#class NewPostView(CreateView):
#    model = Post
#    form_class = PostForm
#    success_url = reverse_lazy('post_list')
#    template_name = 'new_post.html'