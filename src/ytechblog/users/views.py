# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone
from . import forms
from django.views.generic import DetailView


from .models import Article, Profile, Images, Comment, AdvertImages
from datetime import datetime
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.forms import modelformset_factory
from django.contrib import messages

# Create your views here.


#def article_list(request):
    #articles = Article.objects.all().order_by('-date')
    #return render(request, "users/article_list.html", {'articles': articles})

def advert_images(request):
    image = AdvertImages.objects.all()[0]
    advert = image.advert
    thumb = image.thumb.url
    context = {
        'image': image,
        'advert': advert,
        'thumb': thumb,
    }
    return render(request, "users/advert.html", context)



def article_list(request):
    #postss = Article.objects.all().order_by('-created')
    image = AdvertImages.objects.all()
    w = image[0].thumb.url
    v = image[1].thumb.url
    posts = Article.published.all()
    query = request.GET.get('q')
    if query:
        posts = Article.published.filter(
        Q(title__icontains=query)|
        Q(author__username=query)|
        Q(body__icontains=query)
        )
    paginator = Paginator(posts, 12)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if page is None:
        start_index = 0
        end_index = 7
    else:
        (start_index, end_index) = proper_pagination(posts, index=4)

    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        'w': w,
        'v': v,
        
        'posts': posts,
        'page_range': page_range,
    }
    return render(request, 'users/article_list.html', context)



def proper_pagination(posts, index):
    start_index = 0
    end_index = 7
    if posts.number > index:
        start_index = posts.number - index
        end_index = start_index + end_index
    return (start_index, end_index)


#class PostDetail(DetailView):
    #model = Article

    #def get_object(self):
        #object = super(PostDetail, self).get_object()
        #object.view_count += 1
        #object.save()
        #return object



        
def article_details(request, id, slug):
    post = get_object_or_404(Article, id=id, slug=slug)
    comments = Comment.objects.filter(post=post, reply=None).order_by('-id')
    is_liked = False
    is_favourite = False
    if post.likes.filter(id=request.user.id).exists():
        is_liked = True

    if post.favourite.filter(id=request.user.id).exists():
        is_favourite = True

    if request.method == 'POST':
        comment_form = CommentForm(request.POST or None)
        if comment_form.is_valid():
            content = request.POST.get('content')
            reply_id = request.POST.get('comment_id')
            comment_qs = None
            if reply_id:
                comment_qs = Comment.objects.get(id=reply_id)
            comment = Comment.objects.create(post=post, user=request.user, content=content, reply=comment_qs)
            comment.save()
            # return HttpResponseRedirect(post.get_absolute_url())
    else:
        comment_form= CommentForm()

    context = {
        'post': post,
        'is_liked': is_liked,
        'is_favourite': is_favourite,
        'total_likes': post.total_likes(),
        'comments': comments,
        'comment_form': comment_form,
    }
    if request.is_ajax():
        html = render_to_string('users/comments.html', context, request=request)
        return JsonResponse({'form': html})

    return render(request, 'users/article_details.html', context)




#def article_details(request, slug):
    #article = Article.objects.get(slug=slug)
    #context = {
        #"article": article,
        #"user": request.user
    #}
    #return render(request, "users/details.html", context)
    #return HttpResponse(slug)



#def post_favourite_list(request):
        #user = request.user
        #favourite_posts = user.favourite.all()
        #context = {
         #   'favourite_posts': favourite_posts,
       # }
    #return render(request, 'users/post_favourite_list.html', context)

def favourite_post(request, id):
    post = get_object_or_404(Article, id=id)
    if post.favourite.filter(id=request.user.id).exists():
        post.favourite.remove(request.user)
    else:
        post.favourite.add(request.user)
    return HttpResponseRedirect(post.get_absolute_url())


def like_post(request):
    #post = get_object_or_404(Post, id=request.POST.get('post_id'))
    post = get_object_or_404(Article, id=request.POST.get('id'))
    is_liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    context = {
        'post': post,
        'is_liked': is_liked,
        'total_likes': post.total_likes(),
    }
    if request.is_ajax():
        html = render_to_string('users/like_section.html', context, request=request)
        return JsonResponse({'form': html})


@login_required(login_url="/accounts/login/")
def post_create(request):
    ImageFormset = modelformset_factory(Images, fields=('image',), extra=4)
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        formset = ImageFormset(request.POST or None, request.FILES or None)
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            print(formset.cleaned_data)
            for f in formset:
                print(f.cleaned_data)
                try:
                    photo = Images(post=post, image=f.cleaned_data.get('image'))
                    photo.save()
                except Exception as e:
                    break
            messages.success(request, "Post has been successfully created.")
            return redirect('users:article_list')
    else:
        form = PostCreateForm()
        formset = ImageFormset(queryset=Images.objects.none())
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'users/post_create.html', context)




def post_edit(request, id):
    post = get_object_or_404(Article, id=id)
    ImageFormset = modelformset_factory(Images, fields=('image',), extra=4, max_num=4)
    if post.author != request.user:
        raise Http404()
    if request.method == "POST":
        form = PostEditForm(request.POST or None, instance=post)
        formset = ImageFormset(request.POST or None, request.FILES or None)
        if form.is_valid() and formset.is_valid():
            form.save()
            print(formset.cleaned_data)
            data = Images.objects.filter(post=post)
            for index, f in enumerate(formset):
                if f.cleaned_data:
                    if f.cleaned_data['id'] is None:
                        photo = Images(post=post, image=f.cleaned_data.get('image'))
                        photo.save()
                    elif f.cleaned_data['image'] is False:
                        photo = Images.objects.get(id=request.POST.get('form-' + str(index) + '-id'))
                        photo.delete()
                    else:
                        photo = Images(post=post, image=f.cleaned_data.get('image'))
                        d = Images.objects.get(id=data[index].id)
                        d.image = photo.image
                        d.save()
            messages.success(request, "{} has been successfully updated!".format(post.title))
            return HttpResponseRedirect(post.get_absolute_url())
    else:
        form = PostEditForm(instance=post)
        formset = ImageFormset(queryset=Images.objects.filter(post=post))
    context = {
    'form': form,
    'post': post,
    'formset': formset,
    }
    return render(request, 'users/post_edit.html', context)




def post_delete(request, id):
    post = get_object_or_404(Article, id=id)
    if request.user != post.author:
        raise Http404()
    post.delete()
    messages.warning(request, 'post has been successfully deleted!')
    return redirect('users:article_list')




def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    if 'next' in request.POST:
                        return HttpResponseRedirect(reverse(request.POST.get('next')))
                    else:
                        return HttpResponseRedirect(reverse('users:article_list'))
                else:
                    return HttpResponse("User is not active")
            else:
                return HttpResponse("User is None")
    else:
        form = UserLoginForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/login.html', context)


def user_logout(request):
    logout(request)
    return redirect('users:article_list')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'users/register.html', context)


@login_required(login_url="/accounts/login/")
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST or None, instance=request.user)
        profile_form = ProfileEditForm(data=request.POST or None, instance=request.user.profile, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            print(profile_form)
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse("users:edit_profile"))
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/edit_profile.html', context)











#@login_required(login_url="/accounts/login/")
#def comment(request):
	#if request.method == "POST":
		#form = forms.CommentArticle(request.POST, request.FILES)
		#if form.is_valid():
			#instance = form.save(commit=False)
			#instance.author = request.user
			#instance.save()
			#
			#return HttpResponseRedirect(reverse("users:home"))


	#else:
		#form = forms.CommentArticle()
	#return render(request, "users/comment.html", {"form":form})

