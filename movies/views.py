# movies/views.py
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView
from .models import Movie, MovieRating
from django.db.models import Avg, Count


class MovieRatingView(LoginRequiredMixin, TemplateView):
    template_name = 'rate_movie.html'

    def get_object(self):
        rated_movie_ids = MovieRating.objects.filter(user=self.request.user).values_list('movie_id', flat=True)
        movie = Movie.objects.exclude(id__in=rated_movie_ids).first()
        return movie

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()

        if not movie:
            context['all_rated'] = True
            return context

        context['movie'] = movie
        context['rating_choices'] = MovieRating.RATING_CHOICES

        if movie.trailer_url:
            if 'youtube.com/watch?v=' in movie.trailer_url:
                video_id = movie.trailer_url.split('watch?v=')[1].split('&')[0]
                context['youtube_embed_url'] = f"https://www.youtube.com/embed/{video_id}"
            elif 'youtu.be/' in movie.trailer_url:
                video_id = movie.trailer_url.split('youtu.be/')[1].split('?')[0]
                context['youtube_embed_url'] = f"https://www.youtube.com/embed/{video_id}"

        return context

    def post(self, request, *args, **kwargs):
        movie = self.get_object()

        if not movie:
            messages.info(request, 'No movies to rate.')
            return redirect('rate_movie')

        rating = request.POST.get('rating')

        if rating in ['0', '1', '2', '3']:
            if not MovieRating.objects.filter(user=request.user, movie=movie).exists():
                MovieRating.objects.create(
                    user=request.user,
                    movie=movie,
                    rating=rating
                )
                self.update_movie_stats(movie)
                messages.success(request, f'You rated: {movie.title}')

        return redirect('rate_movie')

    def update_movie_stats(self, movie):
        ratings = MovieRating.objects.filter(movie=movie)
        stats = ratings.aggregate(
            average_rating=Avg('rating'),
            total_ratings=Count('id')
        )
        movie.average_rating = round(stats['average_rating'], 2) if stats['average_rating'] else 0
        movie.total_ratings = stats['total_ratings']
        movie.save()