from django.db import models


class User(models.Model):
    userId = models.IntegerField(primary_key=True, db_column="id")
    userLogin = models.CharField(max_length=45, db_column="login", unique=True)
    userPassHash = models.CharField(max_length=64, db_column="passHash")
    username = models.CharField(max_length=45, db_column="username", unique=True)
    userRole = models.CharField(max_length=45, db_column="role")

    class Meta:
        db_table = "user"


class Author(models.Model):
    authorId = models.IntegerField(primary_key=True, db_column="id")
    authorName = models.CharField(max_length=45, db_column="name")
    description = models.CharField(max_length=200, db_column="description")

    class Meta:
        db_table = "author"


class Track(models.Model):
    trackId = models.IntegerField(primary_key=True, db_column="id")
    trackName = models.CharField(max_length=45, db_column="name")
    duration = models.IntegerField(db_column="duration")
    positionInAlbum = models.IntegerField(db_column="positionInAlbum")
    trackLink = models.CharField(max_length=45, db_column="link")

    class Meta:
        db_table = "track"


class Album(models.Model):
    albumId = models.IntegerField(primary_key=True, db_column="id")
    albumName = models.CharField(max_length=45, db_column="name")

    LP = "longPlay"
    EP = "extendedPlay"
    Single = "Single"
    Demo = "Demo"
    Soundtrack = "Soundtrack"
    Tribute = "Tribute"
    albumTypesChoice = [
        (LP, "longPlay"),
        (EP, "extendedPlay"),
        (Single, "Single"),
        (Demo, "Demo"),
        (Soundtrack, "Soundtrack"),
        (Tribute, "Tribute"),
    ]

    albumType = models.CharField(max_length=12, choices=albumTypesChoice, db_column="type")

    albumCoverLink = models.CharField(max_length=45, db_column="coverLink")
    albumDate = models.DateField(db_column="date")
    albumAuthorId = models.IntegerField(db_column="authorId")

    tracks = models.ManyToManyField(Track, db_table="albumhastracks")

    class Meta:
        db_table = "album"



class userliketrack(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    trackId = models.ForeignKey(Track, on_delete=models.CASCADE, db_column="track_id")
    date = models.DateTimeField(db_column="date")

    class Meta:
        db_table = "userliketrack"


class userCheckAlbum(models.Model):
    id = models.IntegerField(primary_key=True, db_column="id")
    userId = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    albumId = models.ForeignKey(Album, on_delete=models.CASCADE, db_column="album_id")
    date = models.DateTimeField(db_column="date")

    class Meta:
        db_table = "usercheckalbum"


class PassChange(models.Model):
    id = models.IntegerField(primary_key=True, db_column="id")
    date = models.DateTimeField(db_column="date")
    newPassHash = models.CharField(max_length=64, db_column="newPassHash")
    userId = models.ForeignKey(User, on_delete=models.CASCADE, db_column="userId")

    class Meta:
        db_table = "passchange"


