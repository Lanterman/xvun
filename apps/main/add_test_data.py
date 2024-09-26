import logging

from random import randint

from django.db.utils import IntegrityError, DataError
from urllib.error import HTTPError

from apps.user.models import User
from apps.main.models import Collection, Link

from apps.user import services as user_services
from apps.main import services as main_services


test_links = [
    "https://lim-english.com/tests/test-po-angliiskomy-dlya-nachinaushih/",
    "https://lim-english.com/tests/test-po-angliiskomy-dlya-3-go-klassa/",
    "https://lim-english.com/tests/test-po-angliiskomy-dlya-4-go-klassa/",
    "https://lim-english.com/tests/test-po-angliiskomy-yaziky-dlya-5-go-klassa/",
    "https://www.youtube.com/",
    "https://www.google.com/imgres?q=photo&imgurl=https%3A%2F%2Fplus.unsplash.com%2Fpremium_photo-1673448391005-d65e815bd026%3Ffm%3Djpg%26q%3D60%26w%3D3000%26ixlib%3Drb-4.0.3%26ixid%3DM3wxMjA3fDB8MHxzZWFyY2h8MXx8cGhvdG98ZW58MHx8MHx8fDA%253D&imgrefurl=https%3A%2F%2Funsplash.com%2Fs%2Fphotos%2Fphoto&docid=AgAT_yR1X6xrJM&tbnid=Dj4nxeFftuZ_QM&vet=12ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECG0QAA..i&w=3000&h=2000&hcb=2&itg=1&ved=2ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECG0QAA",
    "https://www.google.com/imgres?q=photo&imgurl=https%3A%2F%2Fimages.pexels.com%2Fphotos%2F1308881%2Fpexels-photo-1308881.jpeg%3Fcs%3Dsrgb%26dl%3Dpexels-soldiervip-1308881.jpg%26fm%3Djpg&imgrefurl=https%3A%2F%2Fwww.pexels.com%2Fsearch%2Fbeautiful%2F&docid=B51x0PBR9KNzvM&tbnid=66_wyOSzUxatwM&vet=12ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECG4QAA..i&w=6720&h=4480&hcb=2&ved=2ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECG4QAA",
    "https://www.google.com/imgres?q=photo&imgurl=https%3A%2F%2Fbuffer.com%2Fcdn-cgi%2Fimage%2Fw%3D1000%2Cfit%3Dcontain%2Cq%3D90%2Cf%3Dauto%2Flibrary%2Fcontent%2Fimages%2Fsize%2Fw1200%2F2023%2F10%2Ffree-images.jpg&imgrefurl=https%3A%2F%2Fbuffer.com%2Flibrary%2Ffree-images%2F&docid=U9G_8UXPMlqatM&tbnid=5UpJfcabDnVl2M&vet=12ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oFCIABEAA..i&w=1000&h=666&hcb=2&itg=1&ved=2ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oFCIABEAA",
    "https://www.google.com/imgres?q=photo&imgurl=https%3A%2F%2Fi0.wp.com%2Fpicjumbo.com%2Fwp-content%2Fuploads%2Fcamping-on-top-of-the-mountain-during-sunset-free-photo.jpg%3Fw%3D600%26quality%3D80&imgrefurl=https%3A%2F%2Fpicjumbo.com%2F&docid=Kzg7bmtb2MSiyM&tbnid=dJYzWr_317EuiM&vet=12ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECBsQAA..i&w=600&h=376&hcb=2&itg=1&ved=2ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECBsQAA",
    "https://www.youtube.com/watch?v=w8rRhAup4kg",
    "https://www.youtube.com/watch?v=tsbg0eiKU1I&list=RDtsbg0eiKU1I&start_radio=1",
    "https://www.youtube.com/@HowdyhoNet",
    "https://www.youtube.com/watch?v=hc8hW26vuI4",
    "https://www.youtube.com/watch?v=J4tlyR742GA&list=RDJ4tlyR742GA&start_radio=1",
    "https://www.youtube.com/watch?v=fTI7084HtSE",
    "https://hh.ru/resume/98f4675dff098ac0180039ed1f734162367752",
    "https://github.com/Lanterman",
    "https://github.com/Lanterman/seabattle_backend",
    "https://github.com/Lanterman/seabattle_frontend",
    "https://github.com/Lanterman/meeting_website",
    "https://github.com/erikriver/opengraph",
    "https://developer.mozilla.org/ru/docs/Learn/Server-side/Django/Deployment",
    "https://www.tensorflow.org/tutorials/keras/regression#linear_regression_with_multiple_inputs",
    "https://habr.com/ru/articles/770554/",
    "https://www.django-rest-framework.org/",
    "https://www.google.com/imgres?q=photo&imgurl=https%3A%2F%2Fimages.pexels.com%2Fphotos%2F1416736%2Fpexels-photo-1416736.jpeg%3Fcs%3Dsrgb%26dl%3Dpexels-jonas-mohamadi-1416736.jpg%26fm%3Djpg&imgrefurl=https%3A%2F%2Fwww.pexels.com%2Fsearch%2Fkids%2F&docid=gYSZtCKuC-swdM&tbnid=1cSdnQcfm0_VCM&vet=12ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECGMQAA..i&w=4912&h=7360&hcb=2&ved=2ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECGMQAA",
    "https://www.google.com/imgres?q=photo&imgurl=https%3A%2F%2Fwww.befunky.com%2Fimages%2Fprismic%2F32083dff-734b-49a7-bb4d-c0dc512401af_hero-photo-effects-5.jpg%3Fauto%3Davif%2Cwebp%26format%3Djpg%26width%3D896&imgrefurl=https%3A%2F%2Fwww.befunky.com%2Ffeatures%2Fphoto-effects%2F&docid=Ao1a_PBizBtlCM&tbnid=9BOR3eQgag_q4M&vet=12ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECF4QAA..i&w=896&h=504&hcb=2&ved=2ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECF4QAA",
    "https://www.google.com/imgres?q=photo&imgurl=https%3A%2F%2Fcdn.pixabay.com%2Fphoto%2F2014%2F02%2F27%2F16%2F10%2Fflowers-276014_1280.jpg&imgrefurl=https%3A%2F%2Fpixabay.com%2Fphotos%2Fflowers-meadow-sunlight-summer-276014%2F&docid=wqLT8GhLsxbLDM&tbnid=vY6B1urBVzeArM&vet=12ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECFoQAA..i&w=1280&h=814&hcb=2&ved=2ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECFoQAA",
    "https://www.google.com/imgres?q=photo&imgurl=https%3A%2F%2Fstatic.vecteezy.com%2Fsystem%2Fresources%2Fthumbnails%2F026%2F829%2F465%2Fsmall%2Fbeautiful-girl-with-autumn-leaves-photo.jpg&imgrefurl=https%3A%2F%2Fwww.vecteezy.com%2Ffree-photos%2Fbeauty-girl&docid=FJws_VLfyRaiqM&tbnid=Mlm_CVVVNUDsRM&vet=12ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECGgQAA..i&w=271&h=200&hcb=2&itg=1&ved=2ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECGgQAA",
    "https://www.google.com/imgres?q=photo&imgurl=https%3A%2F%2Fphotoscissors.com%2Fimages%2Fsamples%2F1-before.jpg&imgrefurl=https%3A%2F%2Fphotoscissors.com%2F&docid=KufthtopOq8m5M&tbnid=smPuIZrg9wkwqM&vet=12ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECCQQAA..i&w=1280&h=854&hcb=2&itg=1&ved=2ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECCQQAA",
    "https://www.google.com/imgres?q=photo&imgurl=https%3A%2F%2Fstatic-cse.canva.com%2Fblob%2F1257263%2Ftools-feature_photo_background_change_hero_mobile.jpg&imgrefurl=https%3A%2F%2Fwww.canva.com%2Ffeatures%2Fphoto-background-changer%2F&docid=xSyf4if0KGBUWM&tbnid=MTSuwdbxO_Zz8M&vet=12ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECEMQAA..i&w=4096&h=2449&hcb=2&ved=2ahUKEwjimuPNhOCIAxWkZ0EAHXEnI4UQM3oECEMQAA"
]


def add_test_data():
    """Add test data"""

    for i in range(1, 12):
        try:
            User.objects.create(username=f"string{i}", email=f"string{i}@mail.ru",
                hashed_password=user_services.create_hashed_password(f"stringstring{i}"))
            user_services.create_jwttoken(i)
        except IntegrityError:
            logging.warn(f"This user exists. User string{i}")

    for i in range(1, 12):
        try:
            Collection.objects.create(name=f"string{i}", description=f"string{i}", user_id_id=i)
        except IntegrityError:
            logging.warn(f"This collection exists. Collection string{i}")

    collections = Collection.objects.all().select_related("user_id")

    for link in test_links:
        collection = collections[randint(0, len(collections) - 1)]
        
        try:
            data = main_services.get_dict_with_data_from_link(link)
            link = Link.objects.create(title=data["title"], description=data["description"],
                                link=data["link"], image=data["image"],
                                type_of_link=data["type_of_link"], user_id_id=collection.user_id.id)
            
            link.collections.add(collection)
        except IntegrityError:
            logging.warn(f"This link exists. Link: {data["title"]} - {data["link"]}")
        except HTTPError:
            continue
        except DataError as e:
            logging.warn(f"Problem with the size of the type_of_link field. I don't know why. Link: {data["type_of_link"]}")
