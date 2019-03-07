# Generated by Django 2.1.7 on 2019-03-06 05:51

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Billing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cc_info', models.BigIntegerField(default=0)),
                ('next_payment_date', models.DateField(default=django.utils.timezone.now)),
                ('num_sub_slots', models.IntegerField(default=10)),
                ('num_rentals', models.IntegerField(default=0)),
                ('transaction_info', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=20)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='CommentSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_comments', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_messages', models.IntegerField(default=0)),
                ('num_read_messages', models.IntegerField(default=0)),
                ('num_unread_messages', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=20)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('genre', models.CharField(max_length=20)),
                ('release_year', models.IntegerField(default=0)),
                ('studio', models.CharField(max_length=20)),
                ('streaming_service', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField(default='')),
                ('air_date', models.DateField(auto_now=True)),
                ('file_location', models.CharField(max_length=50)),
                ('runtime', models.DurationField(default=0)),
                ('comment_section', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.CommentSection')),
                ('metadata', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.Metadata')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Preferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_opt_in', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RatingSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_of_ratings', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='TVEpisode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(default='')),
                ('air_date', models.DateField(auto_now=True)),
                ('file_location', models.CharField(max_length=50)),
                ('runtime', models.DurationField(default=0)),
                ('title', models.CharField(max_length=25)),
                ('episode_number', models.IntegerField(default=0)),
                ('comment_section', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.CommentSection')),
                ('metadata', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.Metadata')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TVSeason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season_number', models.IntegerField(default=0)),
                ('num_episodes', models.IntegerField(default=0)),
                ('description', models.TextField(default='')),
                ('year', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='TVShow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField(default='')),
                ('air_date', models.DateField(auto_now=True)),
                ('num_seasons', models.IntegerField(default=0)),
                ('comment_section', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.CommentSection')),
                ('metadata', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.Metadata')),
                ('rating_section', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.RatingSection')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=15)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=20)),
                ('email', models.CharField(max_length=30)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now)),
                ('billing', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.Billing')),
                ('comment_section', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.CommentSection')),
                ('inbox', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.Inbox')),
                ('preferences', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.Preferences')),
                ('rentals', models.ManyToManyField(blank=True, to='streaming.Movie')),
                ('subscriptions', models.ManyToManyField(blank=True, to='streaming.TVShow')),
            ],
        ),
        migrations.AddField(
            model_name='tvseason',
            name='part_of',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.TVShow'),
        ),
        migrations.AddField(
            model_name='tvepisode',
            name='part_of',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.TVSeason'),
        ),
        migrations.AddField(
            model_name='tvepisode',
            name='rating_section',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.RatingSection'),
        ),
        migrations.AddField(
            model_name='rating',
            name='part_of',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.RatingSection'),
        ),
        migrations.AddField(
            model_name='rating',
            name='posted_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.User'),
        ),
        migrations.AddField(
            model_name='movie',
            name='rating_section',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.RatingSection'),
        ),
        migrations.AddField(
            model_name='message',
            name='from_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.User'),
        ),
        migrations.AddField(
            model_name='message',
            name='part_of',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.Inbox'),
        ),
        migrations.AddField(
            model_name='comment',
            name='part_of',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.CommentSection'),
        ),
        migrations.AddField(
            model_name='comment',
            name='posted_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.User'),
        ),
        migrations.AddField(
            model_name='actor',
            name='part_of',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.Metadata'),
        ),
    ]