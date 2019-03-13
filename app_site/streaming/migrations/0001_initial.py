# Generated by Django 2.1.7 on 2019-03-12 20:33

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
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
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('part_of', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.Inbox')),
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
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='movie',
            name='rating_section',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.RatingSection'),
        ),
        migrations.AddField(
            model_name='comment',
            name='part_of',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.CommentSection'),
        ),
        migrations.AddField(
            model_name='comment',
            name='posted_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='actor',
            name='part_of',
            field=models.ManyToManyField(blank=True, to='streaming.Metadata'),
        ),
        migrations.AddField(
            model_name='siteuser',
            name='billing',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.Billing'),
        ),
        migrations.AddField(
            model_name='siteuser',
            name='comment_section',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.CommentSection'),
        ),
        migrations.AddField(
            model_name='siteuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='siteuser',
            name='inbox',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.Inbox'),
        ),
        migrations.AddField(
            model_name='siteuser',
            name='preferences',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='streaming.Preferences'),
        ),
        migrations.AddField(
            model_name='siteuser',
            name='rentals',
            field=models.ManyToManyField(blank=True, to='streaming.Movie'),
        ),
        migrations.AddField(
            model_name='siteuser',
            name='subscriptions',
            field=models.ManyToManyField(blank=True, to='streaming.TVShow'),
        ),
        migrations.AddField(
            model_name='siteuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
