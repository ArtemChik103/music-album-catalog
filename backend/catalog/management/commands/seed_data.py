from django.core.management.base import BaseCommand
from django.db import transaction
from catalog.models import Album, AlbumSong, Artist, Song


class Command(BaseCommand):
    help = 'Заполняет базу данных реалистичными демонстрационными данными'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Начало заполнения каталога...'))

        # Очищаем перед сидингом для детерминированности
        AlbumSong.objects.all().delete()
        Album.objects.all().delete()
        Song.objects.all().delete()
        Artist.objects.all().delete()

        # Создаем исполнителей
        queen = Artist.objects.create(name='Queen')
        pink_floyd = Artist.objects.create(name='Pink Floyd')
        daft_punk = Artist.objects.create(name='Daft Punk')
        radiohead = Artist.objects.create(name='Radiohead')

        # Создаем общие песни (которые входят в разные альбомы с разными номерами)
        bohemian_rhapsody = Song.objects.create(title='Bohemian Rhapsody')
        youre_my_best_friend = Song.objects.create(title="You're My Best Friend")
        we_will_rock_you = Song.objects.create(title='We Will Rock You')
        we_are_the_champions = Song.objects.create(title='We Are the Champions')

        time_song = Song.objects.create(title='Time')
        money_song = Song.objects.create(title='Money')
        comfortably_numb = Song.objects.create(title='Comfortably Numb')
        wish_you_were_here = Song.objects.create(title='Wish You Were Here')

        one_more_time = Song.objects.create(title='One More Time')
        harder_better = Song.objects.create(title='Harder, Better, Faster, Stronger')

        paranoid_android = Song.objects.create(title='Paranoid Android')
        karma_police = Song.objects.create(title='Karma Police')
        creep = Song.objects.create(title='Creep')

        # 1. Queen - A Night at the Opera (1975)
        opera = Album.objects.create(
            title='A Night at the Opera',
            artist=queen,
            release_year=1975
        )
        s_death = Song.objects.create(title='Death on Two Legs')
        s_lazing = Song.objects.create(title='Lazing on a Sunday Afternoon')
        s_im_in_love = Song.objects.create(title="I'm in Love with My Car")
        s_god_save = Song.objects.create(title='God Save the Queen')

        AlbumSong.objects.create(album=opera, song=s_death, track_number=1)
        AlbumSong.objects.create(album=opera, song=s_lazing, track_number=2)
        AlbumSong.objects.create(album=opera, song=s_im_in_love, track_number=3)
        AlbumSong.objects.create(album=opera, song=youre_my_best_friend, track_number=4)
        AlbumSong.objects.create(album=opera, song=bohemian_rhapsody, track_number=11)
        AlbumSong.objects.create(album=opera, song=s_god_save, track_number=12)

        # 2. Queen - Greatest Hits (1981)
        # Обратите внимание: Bohemian Rhapsody здесь номер 1, а в Opera был номер 11!
        queen_hits = Album.objects.create(
            title='Greatest Hits',
            artist=queen,
            release_year=1981
        )
        s_bites = Song.objects.create(title='Another One Bites the Dust')
        s_killer = Song.objects.create(title='Killer Queen')
        s_dont_stop = Song.objects.create(title="Don't Stop Me Now")

        AlbumSong.objects.create(album=queen_hits, song=bohemian_rhapsody, track_number=1)
        AlbumSong.objects.create(album=queen_hits, song=s_bites, track_number=2)
        AlbumSong.objects.create(album=queen_hits, song=s_killer, track_number=3)
        AlbumSong.objects.create(album=queen_hits, song=youre_my_best_friend, track_number=4)
        AlbumSong.objects.create(album=queen_hits, song=s_dont_stop, track_number=5)
        AlbumSong.objects.create(album=queen_hits, song=we_will_rock_you, track_number=6)
        AlbumSong.objects.create(album=queen_hits, song=we_are_the_champions, track_number=7)

        # 3. Queen - News of the World (1977)
        queen_news = Album.objects.create(
            title='News of the World',
            artist=queen,
            release_year=1977
        )
        s_sheer = Song.objects.create(title='Sheer Heart Attack')
        s_wings = Song.objects.create(title='Spread Your Wings')

        AlbumSong.objects.create(album=queen_news, song=we_will_rock_you, track_number=1)
        AlbumSong.objects.create(album=queen_news, song=we_are_the_champions, track_number=2)
        AlbumSong.objects.create(album=queen_news, song=s_sheer, track_number=3)
        AlbumSong.objects.create(album=queen_news, song=s_wings, track_number=4)

        # 4. Pink Floyd - The Dark Side of the Moon (1973)
        dark_side = Album.objects.create(
            title='The Dark Side of the Moon',
            artist=pink_floyd,
            release_year=1973
        )
        s_breathe = Song.objects.create(title='Breathe (In the Air)')
        s_great_gig = Song.objects.create(title='The Great Gig in the Sky')
        s_brain = Song.objects.create(title='Brain Damage')
        s_eclipse = Song.objects.create(title='Eclipse')

        AlbumSong.objects.create(album=dark_side, song=s_breathe, track_number=1)
        AlbumSong.objects.create(album=dark_side, song=time_song, track_number=4)
        AlbumSong.objects.create(album=dark_side, song=s_great_gig, track_number=5)
        AlbumSong.objects.create(album=dark_side, song=money_song, track_number=6)
        AlbumSong.objects.create(album=dark_side, song=s_brain, track_number=9)
        AlbumSong.objects.create(album=dark_side, song=s_eclipse, track_number=10)

        # 5. Pink Floyd - Echoes: The Best of Pink Floyd (2001)
        # Time здесь трек 2, Money - трек 4, Comfortably Numb - трек 5
        echoes = Album.objects.create(
            title='Echoes: The Best of Pink Floyd',
            artist=pink_floyd,
            release_year=2001
        )
        s_astronomy = Song.objects.create(title='Astronomy Domine')

        AlbumSong.objects.create(album=echoes, song=s_astronomy, track_number=1)
        AlbumSong.objects.create(album=echoes, song=time_song, track_number=2)
        AlbumSong.objects.create(album=echoes, song=wish_you_were_here, track_number=3)
        AlbumSong.objects.create(album=echoes, song=money_song, track_number=4)
        AlbumSong.objects.create(album=echoes, song=comfortably_numb, track_number=5)

        # 6. Pink Floyd - The Wall (1979)
        the_wall = Album.objects.create(
            title='The Wall',
            artist=pink_floyd,
            release_year=1979
        )
        s_in_flesh = Song.objects.create(title='In the Flesh?')
        s_brick = Song.objects.create(title='Another Brick in the Wall, Pt. 2')
        s_hey_you = Song.objects.create(title='Hey You')

        AlbumSong.objects.create(album=the_wall, song=s_in_flesh, track_number=1)
        AlbumSong.objects.create(album=the_wall, song=s_brick, track_number=2)
        AlbumSong.objects.create(album=the_wall, song=s_hey_you, track_number=3)
        AlbumSong.objects.create(album=the_wall, song=comfortably_numb, track_number=6)

        # 7. Daft Punk - Discovery (2001)
        discovery = Album.objects.create(
            title='Discovery',
            artist=daft_punk,
            release_year=2001
        )
        s_aero = Song.objects.create(title='Aerodynamic')
        s_digital = Song.objects.create(title='Digital Love')

        AlbumSong.objects.create(album=discovery, song=one_more_time, track_number=1)
        AlbumSong.objects.create(album=discovery, song=s_aero, track_number=2)
        AlbumSong.objects.create(album=discovery, song=s_digital, track_number=3)
        AlbumSong.objects.create(album=discovery, song=harder_better, track_number=4)

        # 8. Daft Punk - Alive 2007 (2007)
        alive_2007 = Album.objects.create(
            title='Alive 2007',
            artist=daft_punk,
            release_year=2007
        )
        s_robot = Song.objects.create(title='Robot Rock / Oh Yeah')
        s_touch = Song.objects.create(title='Touch It / Technologic')

        AlbumSong.objects.create(album=alive_2007, song=s_robot, track_number=1)
        AlbumSong.objects.create(album=alive_2007, song=s_touch, track_number=2)
        AlbumSong.objects.create(album=alive_2007, song=harder_better, track_number=3)
        AlbumSong.objects.create(album=alive_2007, song=one_more_time, track_number=5)

        # 9. Radiohead - OK Computer (1997)
        ok_computer = Album.objects.create(
            title='OK Computer',
            artist=radiohead,
            release_year=1997
        )
        s_airbag = Song.objects.create(title='Airbag')
        s_subterranean = Song.objects.create(title='Subterranean Homesick Alien')
        s_no_surprises = Song.objects.create(title='No Surprises')

        AlbumSong.objects.create(album=ok_computer, song=s_airbag, track_number=1)
        AlbumSong.objects.create(album=ok_computer, song=paranoid_android, track_number=2)
        AlbumSong.objects.create(album=ok_computer, song=s_subterranean, track_number=3)
        AlbumSong.objects.create(album=ok_computer, song=karma_police, track_number=6)
        AlbumSong.objects.create(album=ok_computer, song=s_no_surprises, track_number=10)

        # 10. Radiohead - The Best Of (2008)
        radiohead_best = Album.objects.create(
            title='The Best Of',
            artist=radiohead,
            release_year=2008
        )
        s_high_dry = Song.objects.create(title='High and Dry')

        AlbumSong.objects.create(album=radiohead_best, song=creep, track_number=1)
        AlbumSong.objects.create(album=radiohead_best, song=paranoid_android, track_number=2)
        AlbumSong.objects.create(album=radiohead_best, song=karma_police, track_number=3)
        AlbumSong.objects.create(album=radiohead_best, song=s_high_dry, track_number=4)

        self.stdout.write(
            self.style.SUCCESS(
                f'Каталог успешно заполнен: {Artist.objects.count()} артистов, '
                f'{Album.objects.count()} альбомов, {Song.objects.count()} песен, '
                f'{AlbumSong.objects.count()} треков.'
            )
        )
