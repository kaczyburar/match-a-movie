from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Movie, MovieRating
from django.contrib import messages


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
        if rating in ['0', '1', '2', 'watched']:
            if not MovieRating.objects.filter(user=request.user, movie=movie).exists():

                if rating == 'watched':
                    MovieRating.objects.create(
                        user=request.user,
                        movie=movie,
                        rating=None,
                        watched=True,
                    )
                else:
                    MovieRating.objects.create(
                        user=request.user,
                        movie=movie,
                        rating=rating,
                        watched=False
                    )


                self.update_movie_stats(movie)

        return redirect('rate_movie')

    def update_movie_stats(self, movie):
        ratings = MovieRating.objects.filter(movie=movie, rating__isnull=False)

        if ratings.exists():
            rating_values = [int(r.rating) for r in ratings]
            average_rating = sum(rating_values) / len(rating_values)
            movie.average_rating = round(average_rating, 2)
            movie.total_ratings = len(rating_values)
        else:
            movie.average_rating = 0.00
            movie.total_ratings = 0

        movie.save()