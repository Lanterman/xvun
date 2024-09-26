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
            logging.warn(f"This link exists. Link: {data['title']} - {data['link']}")
        except HTTPError:
            continue
        except DataError as e:
            logging.warn(f"Problem with the size of the type_of_link field. I don't know why. Link: {data['type_of_link']}")
