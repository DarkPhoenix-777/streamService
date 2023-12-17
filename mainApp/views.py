from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from .forms import loginForm, registerForm
from .models import User, Author, Album, Track, userliketrack, userCheckAlbum, PassChange
from django.utils.timezone import make_aware
import datetime


def isAJAX(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def checkSession(request):
    try:
        temp = request.session["login"]
        return True
    except KeyError:
        return False


def saveAlbumCover(file, name, destinationPath):
    with open("mainApp/" + "static/" + destinationPath + "/" + name + ".jpg", 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return destinationPath + "/" + name + ".jpg"


def index(request):
    try:
        d = {"sessionData": request.session}
    except KeyError:
        d = {"sessionData": False}
    albums = Album.objects.all()
    arr = []
    for i, album in enumerate(albums):
        albData = {
            "albId": album.albumId,
            "albName": album.albumName,
            "authorName": Author.objects.get(authorId=album.albumAuthorId).authorName
        }
        arr.append((albData, len(userCheckAlbum.objects.filter(albumId=album.albumId))))

    top10 = sorted(arr, key=lambda x: x[1], reverse=True)[:min(10, len(albums))]

    d["albums"] = top10
    if checkSession(request):
        user = User.objects.get(userLogin=request.session["login"])
        if user.userRole == "Admin" or user.userRole == "Moderator":
            request.session["isModerator"] = True
        else:
            request.session["isModerator"] = False
        if user.userRole == "Admin":
            request.session["isAdmin"] = True
        else:
            request.session["isAdmin"] = False
    return render(request, "index.html", d)


def checkPassAndLogin(request):
    logForm = loginForm()
    if request.method != "POST":
        try:
            temp = request.session["login"]
            return redirect("/")
        except:
            return render(request, "login.html", {"form": logForm, "isWrongLogin": False, "isWrongPass": False})
    else:
        login = request.POST.get("login")
        password = request.POST.get("password")

        try:
            temp = User.objects.get(userLogin=login)
        except:
            return JsonResponse({"isWrongLogin": True, "isWrongPass": False})

        try:
            temp = User.objects.get(userPassHash=password)
        except:
            print(password)
            return JsonResponse({"isWrongLogin": False, "isWrongPass": True})

        user = User.objects.get(userLogin=login)
        request.session["login"] = user.userLogin
        if user.userRole == "admin" or user.userRole == "moderator":
            request.session["isModerator"] = True
        else:
            request.session["isModerator"] = False
        if user.userRole == "admin":
            request.session["isAdmin"] = True
        else:
            request.session["isAdmin"] = False
        return redirect("/")


def changePass(request):
    if not request.session["login"]: redirect("login")
    if request.method != "POST":
        return render(request, "changePass.html")
    else:
        user = User.objects.get(userLogin=request.session["login"])
        if isAJAX(request):
            oldPassHash = request.POST.get("oldPass")
            print(user.userPassHash)
            print(oldPassHash)
            if user.userPassHash == oldPassHash:
                newPassHash = request.POST.get("newPass1")
                user.userPassHash = newPassHash
                newPassChange = PassChange(date=make_aware(datetime.datetime.now()),
                                           newPassHash=newPassHash, userId_id=user.userId)
                user.save()
                newPassChange.save()
                return JsonResponse({"isWrongPass": False})
            else:
                return JsonResponse({"isWrongPass": True})


def logout(request):
    try:
        del request.session["login"]
        del request.session["isModerator"]
        del request.session["isAdmin"]
    except KeyError:
        pass

    return redirect("/")


def addAuthor(request):
    try:
        temp = request.session["login"]
    except:
        return redirect("login")

    if not request.session["isModerator"]: return redirect("/")
    if request.method != "POST":
        return render(request, "add/addAuthor.html")
    else:
        name = request.POST.get("AuthorName")
        descr = request.POST.get("AuthorDescription")
        try:
            temp = Author.objects.get(authorName=name)
            return render(request, "add/addAuthor.html", {"msg": "Группа с таким названием уже существует"})
        except:
            currAuthor = Author(authorName=name, description=descr)
            currAuthor.save()
            return render(request, "add/addAuthor.html", {"msg": "Успешно добавлено"})


def autocompleteAuthor(request):
    if isAJAX(request):
        q = request.GET.get("search", "")
        authorNames = Author.objects.filter(authorName__icontains=q).values_list('authorName', flat=True)

        data = {
            "authorNames": list(authorNames)
        }
        return JsonResponse(data)


def viewAuthor(request):
    authorId = request.GET.get("id")

    try:
        login = request.session["login"]
    except:
        login = False

    try:
        author = Author.objects.get(authorId=authorId)
        return render(request, "author.html", {"login": login, "authorId": authorId,
                                               "authorName": author.authorName, "description": author.description})
    except:
        return render(request, "author.html", {"err": True})


def editAuthor(request):
    try:
        temp = request.session["login"]
    except:
        return redirect("login")

    if not request.session["isModerator"]: return redirect("/")
    authorId = request.GET.get("id")
    if request.method != "POST":
        try:
            author = Author.objects.get(authorId=authorId)
        except:
            return render(request, "edit/editAuthor.html", {"err": True})

        data = {
            "err": False,
            "authorId": author.authorId,
            "authorName": author.authorName,
            "description": author.description
        }
        return render(request, "edit/editAuthor.html", data)
    else:
        authorName = request.POST.get("authorName")
        authorDescr = request.POST.get("authorDescription")

        alb = Author.objects.filter(authorId=authorId) \
            .update(authorId=authorId, authorName=authorName, description=authorDescr)

        return redirect(f"/author?id={authorId}")


def register(request):
    if request.method != "POST":
        try:
            temp = request.session["login"]
            return redirect("/")
        except:
            return render(request, "add/registration.html", {"form": registerForm, "loginIsTaken": False})
    else:
        login = request.POST.get("login")
        passHash = request.POST.get("passHash")
        username = request.POST.get("username")
        role = "User"

        try:
            temp = User.objects.get(userLogin=login)
            return JsonResponse({"loginIsTaken": True})
        except:
            newUser = User(userLogin=login, userPassHash=passHash, username=username, userRole=role)
            newUser.save()
            request.session["login"] = newUser.userLogin
            return redirect("/")


def viewAlbum(request):
    albumId = request.GET.get("id")
    try:
        album = Album.objects.get(albumId=albumId)
    except:
        return render(request, "album.html", {"err": True})

    try:
        login = request.session["login"]
    except:
        login = False
    tracks = []
    for i, track in enumerate(album.tracks.all()):
        if track.duration % 60 < 10:
            d = f"{track.duration // 60}:0{track.duration % 60}"
        else:
            d = f"{track.duration // 60}:{track.duration % 60}"

        if not login:
            trackIsLiked = False
        else:
            try:
                userliketrack.objects.get(trackId=track.trackId)
                trackIsLiked = True
            except:
                trackIsLiked = False
        tracks.append((i + 1, track.trackName, d, trackIsLiked, track.trackId))
        print((i + 1, track.trackName, d, trackIsLiked, track.trackId))

    data = {"err": False,
            "login": login,
            "albumId": album.albumId,
            "albumName": album.albumName,
            "albumAuthorId": album.albumAuthorId,
            "albumAuthor": Author.objects.get(authorId=album.albumAuthorId).authorName,
            "coverLink": album.albumCoverLink,
            "date": album.albumDate,
            "tracks": tracks}
    return render(request, "album.html", data)


def addAlbum(request):
    try:
        temp = request.session["login"]
    except:
        return redirect("login")

    if not request.session["isModerator"]: return redirect("/")
    if request.method != "POST":
        return render(request, "add/addAlbum.html")
    else:
        alName = request.POST.get("AlbumName")
        alType = request.POST.get("AlbumType")
        alCover = request.FILES.get("AlbumCover")
        alDate = request.POST.get("AlbumDate")
        countTracks = int(request.POST.get("countTracks"))
        alAuthorName = request.POST.get("AlbumAuthor")
        alAuthorId = Author.objects.get(authorName=alAuthorName).authorId
        if len(Album.objects.filter(albumName=alName, albumAuthorId=alAuthorId)) != 0:
            return render(request, "add/addAlbum.html",
                          {"msg": "Альбом с таким названием у исполнителя уже существует"})
        else:
            alb = Album(albumName=alName, albumType=alType, albumCoverLink="covers/basicCover.png",
                        albumDate=alDate, albumAuthorId=alAuthorId)
            alb.save()
            alb = Album.objects.filter(albumName=alName, albumAuthorId=alAuthorId)[0]
            print(alCover)
            if alCover:
                alCoverLink = saveAlbumCover(alCover, "cover" + str(alb.albumId), "covers")
                alb.albumCoverLink=alCoverLink
                #alb = Album.objects.filter(albumId=alb.albumId)[0]
                print(alb.albumCoverLink)
                alb.save()
            for i in range(1, countTracks + 1):
                trName = request.POST.get("addTrack" + str(i))
                print(trName)
                trDuration = request.POST.get("durationTrack" + str(i))
                trLink = '-'
                newTrack = Track.objects.create(trackName=trName, duration=trDuration, trackLink=trLink,
                                                positionInAlbum=i)
                newTrack = Track.objects.filter(trackName=trName, duration=trDuration, trackLink=trLink,
                                                positionInAlbum=i)[0]
                alb.tracks.add(newTrack)
                alb.save()
            return render(request, "add/addAlbum.html", {"msg": "Успешно добавлено"})


def editAlbum(request):
    try:
        temp = request.session["login"]
    except:
        return redirect("login")

    if not request.session["isModerator"]: return redirect("/")
    albumId = request.GET.get("id")
    if request.method != "POST":
        try:
            album = Album.objects.get(albumId=albumId)
        except:
            return render(request, "edit/editAlbum.html", {"err": True})

        tracks = album.tracks.all()
        tracksData = []
        for i, track in enumerate(tracks):
            tracksData.append((i + 1, track.trackName, track.duration))

        data = {"err": False,
                "albumId": album.albumId,
                "albumName": album.albumName,
                "albumAuthor": Author.objects.get(authorId=album.albumAuthorId).authorName,
                "coverLink": album.albumCoverLink,
                "date": album.albumDate.strftime('%Y-%m-%d'),
                "tracks": tracksData,
                "tracksCount": len(tracksData)}

        return render(request, "edit/editAlbum.html", data)
    else:
        alName = request.POST.get("AlbumName")
        alType = request.POST.get("AlbumType")
        alCover = request.FILES.get("AlbumCover")
        alDate = request.POST.get("AlbumDate")
        countTracks = int(request.POST.get("countTracks"))
        alAuthorName = request.POST.get("AlbumAuthor")
        alAuthorId = Author.objects.get(authorName=alAuthorName).authorId

        if alCover is None:
            alb = Album.objects.filter(albumId=albumId) \
                .update(albumId=albumId, albumName=alName, albumType=alType,
                        albumDate=alDate, albumAuthorId=alAuthorId)
        else:
            alb = Album.objects.filter(albumId=albumId) \
                .update(albumId=albumId, albumName=alName, albumType=alType,
                        albumCoverLink=saveAlbumCover(alCover, "cover" + str(albumId), "covers"),
                        albumDate=alDate, albumAuthorId=alAuthorId)

        alb = Album.objects.get(albumId=albumId)

        newTracksIds = []
        for i in range(1, countTracks + 1):
            trName = request.POST.get("addTrack" + str(i))
            trDuration = request.POST.get("durationTrack" + str(i))
            trLink = '-'
            try:
                newTrack = Track.objects.filter(trackName=trName, duration=trDuration, trackLink=trLink)[0]
                newTrack.positionInAlbum = i
                newTrack.save()
                newTracksIds.append(newTrack.trackId)

            except:
                newTrack = Track.objects.create(trackName=trName, duration=trDuration, trackLink=trLink,
                                                positionInAlbum=i)
                newTrack = Track.objects.filter(trackName=trName, duration=trDuration, trackLink=trLink,
                                                positionInAlbum=i)[0]
                alb.tracks.add(newTrack)
                newTracksIds.append(newTrack.trackId)

            albTracksIds = alb.tracks.all().values_list("trackId", flat=True)

            alb.save()
        for j in albTracksIds:
            if j not in newTracksIds:
                delTrack = Track.objects.get(trackId=j)
                alb.tracks.remove(delTrack)
        alb.save()

        return redirect(f"/album?id={alb.albumId}")


def deleteAlbum(request):
    try:
        temp = request.session["login"]
    except:
        return redirect("login")

    if not request.session["isModerator"]: return redirect("/")
    AlbumId = request.GET.get("id")
    try:
        login = request.session["login"]
    except:
        return redirect("login")
    if login != "admin":
        return redirect("/")
    else:
        if request.method == "POST":
            alb = Album.objects.get(albumId=AlbumId)
            tracks = alb.tracks.all()
            tracks.delete()
            alb.delete()
            return redirect("/")
        else:
            return render(request, "delete/deleteAlbum.html")


def lk(request):
    try:
        temp = request.session["login"]
    except:
        return redirect("login")

    user = User.objects.filter(userLogin=request.session["login"])[0]
    data = {
        "login": user.userLogin,
        "username": user.username,
        "role": user.userRole,
        "likedTracks": []
    }
    likedTracks = Track.objects.filter(userliketrack__userId__lte=user.userId)
    for i, track in enumerate(likedTracks):
        likeDate = userliketrack.objects.get(trackId=track.trackId).date
        alb = Album.objects.filter(tracks=track.trackId)[0]
        albumLink = f"<a href=album?id={alb.albumId}> {alb.albumName}</a>"
        author = Author.objects.get(authorId=alb.albumAuthorId)
        authorLink = f"<a href=author?id={author.authorId}> {author.authorName}</a>"
        data["likedTracks"].append((i, authorLink, track.trackName, albumLink, likeDate, track.trackId))
    return render(request, "lk.html", data)


def likeOrDislikeTrack(request):
    if not checkSession(request):
        return JsonResponse({"isLogin": False})
    user = User.objects.filter(userLogin=request.session["login"])[0]
    trackId = request.GET.get("trackId")
    track = Track.objects.get(trackId=trackId)
    likedTracksIds = [likedTrack.trackId for likedTrack in Track.objects.filter(userliketrack__userId__lte=user.userId)]
    if track.trackId in likedTracksIds:
        delLike = userliketrack.objects.get(userId=user.userId, trackId=track.trackId)
        delLike.delete()
    else:
        newLike = userliketrack(userId_id=user.userId, trackId_id=track.trackId,
                                date=make_aware(datetime.datetime.now()))
        newLike.save()
    return JsonResponse({"isLogin": True})


def checkAlbum(request):
    if request.session["login"]:
        albumId = request.GET.get("albumId")
        user = User.objects.get(userLogin=request.session["login"])
        newCheck = userCheckAlbum(userId_id=user.userId, albumId_id=albumId, date=make_aware(datetime.datetime.now()))
        newCheck.save()
        print(f"User: {user.userLogin} checked album id: {albumId}")
    return HttpResponse()


def search(request):
    if request.method != "GET":
        return render(request, "search.html")
    else:
        searchType = request.GET.get("selectSearch")
        searchText = request.GET.get("searchField")
        try:
            searchPage = int(request.GET.get("page"))
        except:
            searchPage = 0

        if not searchText:
            return render(request, "search.html")

        rowsOnPage = 10
        data = {
            "page": searchPage,
            "pagesCount": range(0),
            "objects": [],
            "type": "",
            "query": searchText
        }
        if searchType == "Album":
            selectedObjects = Album.objects.filter(
                albumName__icontains=searchText)[rowsOnPage * searchPage:rowsOnPage * searchPage + rowsOnPage]
            data["pagesCount"] = range(len(Album.objects.filter(albumName__icontains=searchText)) // rowsOnPage)
            data["type"] = "Album"
            # автор/ название(со ссылкой) /дата выхода/ тип
            for album in selectedObjects:
                link = f"<a href=album?id={album.albumId}> {album.albumName}</a>"
                authorLink = f"<a href=author?id={album.albumAuthorId}>{Author.objects.get(authorId=album.albumAuthorId).authorName}</a>"
                data["objects"].append((authorLink, link, album.albumDate, album.albumType))

        if searchType == "Track":
            selectedObjects = Track.objects.filter(
                trackName__icontains=searchText)[rowsOnPage * searchPage:rowsOnPage * searchPage + rowsOnPage]
            data["pagesCount"] = range(len(Track.objects.filter(trackName__icontains=searchText)) // rowsOnPage)
            # Название/ длительность/ альбом(со ссылкой)
            data["type"] = "Track"
            likedTracksIds = []
            if 'request.session["login"]' in globals():
                user = User.objects.get(userLogin=request.session["login"])
                likedTracksIds = [likedTrack.trackId for likedTrack in
                                  Track.objects.filter(userliketrack__userId__lte=user.userId)]

            for track in selectedObjects:
                albumLink = ""
                alb = Album.objects.filter(tracks=track.trackId)
                if len(alb) == 1:
                    albumLink = f"<a href=album?id={alb[0].albumId}> {alb[0].albumName}</a>"
                else:
                    for j in range(len(alb)):
                        albumLink += f"<a href=album?id={alb[j].albumId}> " \
                                     f"{alb[j].albumName}</a>,"
                duration = f"{track.duration // 60}:{track.duration % 60}"
                isLiked = False
                if track.trackId in likedTracksIds:
                    isLiked = True
                data["objects"].append((track.trackName, duration, albumLink, isLiked, track.trackId))

        if searchType == "Author":
            selectedObjects = Author.objects.filter(
                authorName__icontains=searchText)[rowsOnPage * searchPage:rowsOnPage * searchPage + rowsOnPage]
            data["pagesCount"] = range(len(Author.objects.filter(authorName__icontains=searchText)) // rowsOnPage)
            # имя(со ссылкой)
            data["type"] = "Author"
            for author in selectedObjects:
                link = f"<a href=author?id={author.authorId}> {author.authorName}</a>"
                data["objects"].append(link)

        data["len"] = len(data["objects"])
        return render(request, "search.html", data)


def adminPanel(request):
    if request.session["login"] and request.session["isAdmin"]:
        return render(request, "adminPanel.html")
    else:
        return redirect("/")


def adminUsers(request):
    if not request.session["login"]:
        return redirect("login")
    if not request.session["isAdmin"]:
        return redirect("/")
    searchText = request.GET.get("search")


    if request.method == "POST":
        userId = request.POST.get("userId")
        newUsername = request.POST.get("username" + str(userId))
        newLogin = request.POST.get("login" + str(userId))
        newPassHash = request.POST.get("passhash" + str(userId))
        newRole = request.POST.get("userRole" + str(userId))
        user = User.objects.get(userId=userId)
        user.username = newUsername
        user.userLogin = newLogin
        user.userPassHash = newPassHash
        user.userRole = newRole
        user.save()
        print(userId, newUsername, newLogin, newPassHash, newRole)

    if searchText is None:
        users = User.objects.all()
    else:
        users = User.objects.filter(username__icontains=searchText)

    selectedObjects = []
    for user in users:
        isUser = True if user.userRole == "User" else False
        isModerator = True if user.userRole == "Moderator" else False
        isAdmin = True if user.userRole == "Admin" else False
        selectedObjects.append((user.userId, user.username, user.userLogin, user.userPassHash,
                                    isUser, isModerator, isAdmin))
    data = {
        "objects": selectedObjects,
        "objectsCount": len(selectedObjects),
        "query": searchText
    }
    return render(request, "adminUsers.html", data)

def delUser(request):
    if isAJAX(request) and request.session["isAdmin"]:
        userId = request.GET.get("userId")
        print(f"Delete user: {userId}")
        user = User.objects.get(userId=userId)
        if user.userRole != "admin":
            user.delete()
            return HttpResponse(True)
        else:
            return HttpResponse(False)
