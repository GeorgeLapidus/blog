from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render
from rest_framework.views import APIView

from account.models import BlogUser
from .forms import CommentForm, EmailsForm, AnswerCommentForm
from .models import Category, Post, Comment, Emails, AnswerComment, Like
from .serializers import CategoryModelSerializer, PostModelSerializer, CommentModelSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response


def start_page(request):
    """Функция вывода стартовой страницы"""

    categories = Category.objects.all()
    posts = Post.objects.all()
    form = EmailsForm()
    if request.method == 'POST':
        new_email = EmailsForm(request.POST)
        if new_email.is_valid():
            new_email.save()
            return render(request, 'start_page.html',
                          {'categories': categories, 'posts': posts, 'form': form, 'message': "Ваш email сохранен!"})
    context = {'categories': categories, 'posts': posts, 'form': form}
    return render(request, 'start_page.html', context)


def post_detail(request, id):
    """Фукция вывода детальной информации новости"""

    categories = Category.objects.all()
    post_info = Post.objects.filter(id=id)
    post = post_info[0]
    post_additional_images = post.postadditionalimage_set.all()

    'Счётчик просмотров'
    if request.method == 'GET':
        post.views += 1

        'Счётчик лайков'
        if request.GET.get('Likes') == 'Likes':
            if request.user.username:
                user = BlogUser.objects.get(username=request.user.username)
                category_id = post.category_id
                like = Like.objects.filter(post_id=id, category_id=category_id, user=user)
                if len(like) > 0:
                    like.delete()
                    post.likes -= 1
                else:
                    like = Like(post_id=id, category_id=category_id, user=user)
                    like.save()
                    post.likes += 1
                post_info.update(likes=post.likes)
            post.views -= 1

        post_info.update(views=post.views)

    form = CommentForm()
    comments = Comment.objects.filter(is_publish='True', post_id=id)
    answer_comments = AnswerComment.objects.filter(is_publish='True')
    if request.user.username:
        user = BlogUser.objects.get(username=request.user.username)
        if request.method == 'POST':
            comment = Comment(text=request.POST.get("text"), post_id=id, user=user)
            comment.save()
            return render(request, 'success_add_comment.html')
    context = {'categories': categories, 'post': post, 'post_additional_images': post_additional_images, 'form': form,
               'comments': comments, 'answer_comments': answer_comments}
    return render(request, 'post_detail.html', context)


# import telebot
# bot = telebot.TeleBot('5344465413:AAGG8i1-QKfIoQTzfEjQVB8pb9YAxZVp9Mw')
# CHANNEL_NAME = '@https://t.me/+CJtzLP2spNk5YjIy'

@receiver(post_save, sender=Comment)
def send_bot_message(sender, **kwargs):
    """Сигнал об оставленном комментарии"""

    print("Оставили комментарий")
    # bot.send_message(CHANNEL_NAME, "Оставили комментарий")

    send_mail(
        'Оставили комментарий',
        'Вам оставили комментарий на БЛОГ ITECH http://127.0.0.1:8000/',
        'python.project2012@gmail.com',
        ['python.project2012@gmail.com', 'shvedovska_vera@mail.ru'],
        fail_silently=False)
    print("Письмо отправлено с помощью сигнала - оставили комментарий")


@receiver(post_save, sender=Post)
def listen_to_posts(sender, **kwargs):
    """Сигнал для отправки уведомлений о выходе нового поста"""

    emails_form = Emails.objects.all()
    emails_register = BlogUser.objects.filter(send_message=True).exclude(is_superuser=True)
    a = []
    if emails_form:
        for e in emails_form:
            a.append(e.email)
    if emails_register:
        for e in emails_register:
            a.append(e.email)
    recipients = list(set(a))
    subject = 'Новый пост в БЛОГЕ компании ITEC'
    # html_message = render_to_string('message.html')
    # plain_message = strip_tags(html_message)
    plain_message = "Новый пост на сайте айтек"
    from_email = 'python.project2012@gmail.com'
    # send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    send_mail(subject, plain_message, from_email, recipients)
    print("Рассылка уведомлений")


def answer_comment(request, id):
    """Функция ответа на комментарий"""

    form = AnswerCommentForm()
    comment = Comment.objects.get(id=id)
    if request.user.username:
        user = BlogUser.objects.get(username=request.user.username)
        if request.method == 'POST':
            answer_comment = AnswerComment(text=request.POST.get("text"), comment_id=id, user=user)
            answer_comment.save()
            return render(request, 'success_add_comment.html')
    context = {'form': form, 'comment': comment}
    return render(request, "answer_comment.html", context)


@receiver(post_save, sender=AnswerComment)
def send_message_about_answer(sender, **kwargs):
    """Сигнал об оставленном ответе на комментарии"""

    print("Оставили ответ на комментарий")
    send_mail(
        'Оставили ответ на комментарий',
        'Вам оставили ответ на комментарий на БЛОГ ITECH http://127.0.0.1:8000/',
        'python.project2012@gmail.com',
        ['python.project2012@gmail.com', 'shvedovska_vera@mail.ru'],
        fail_silently=False)
    print("Письмо отправлено с помощью сигнала - ответ на комментарий")


def category_post(request, category_id):
    categories = Category.objects.all()
    posts = Post.objects.filter(category_id=category_id)
    context = {'categories': categories, 'posts': posts}
    return render(request, "category_post.html", context)


###### REST API ##########
class CategoryAll(APIView):
    """api_rest вывод всех категорий блога (get), добавление категории (post), обновление категории (put)"""

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategoryModelSerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategoryModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)

    def put(self, request):
        categories = Category.objects.all()
        serializer = CategoryModelSerializer(categories, many=True)
        instance = Category.objects.get(id=request.data.get("id"))
        s = CategoryModelSerializer(instance, data=request.data)
        if s.is_valid():
            s.save()
        return Response(serializer.data)



class CategoryOne(APIView):
    """api_rest вывод одной новости блога"""

    def get(self, request, id):
        category = Category.objects.get(id=id)
        serializer = CategoryModelSerializer(category)
        return Response(serializer.data)

class PostAll(APIView):
    """api_rest вывод всех новостей блога"""

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostModelSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)


class PostOne(APIView):
    """api_rest вывод одной новости блога"""

    def get(self, request, id):
        post = Post.objects.get(id=id)
        serializer = PostModelSerializer(post)
        return Response(serializer.data)


class CommentByPost(APIView):
    """api_rest вывод всех комментариев по id новости"""

    def get(self, request, id):
        comments = Post.objects.get(id=id).comment_set.all()
        serializer = CommentModelSerializer(comments, many=True)
        return Response(serializer.data)



class CommentAll(APIView):
    """api_rest вывод всех комментариев блога"""

    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentModelSerializer(comments, many=True)
        return Response(serializer.data)

class CommentOne(APIView):
    """api_rest вывод одного комментария"""

    def get(self, request, id):
        comments = Comment.objects.get(id=id)
        serializer = CommentModelSerializer(comments)
        return Response(serializer.data)

