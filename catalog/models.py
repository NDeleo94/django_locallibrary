from django.db import close_old_connections, models
from django.db.models.base import Model
from django.db.models.deletion import SET_NULL
from django.db.models.expressions import F
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
class Genre(models.Model):
    """
    Modelo que representa un genero literario (p. ej. ciencia ficcion, poesia, etc.).
    """
    name = models.CharField(max_length=200, help_text="Ingrese el nombre del genero (p. ej. Ciencia Ficcion, Poesia Francesa etc.)")

    def __str__(self) -> str:
        """
        Cadena que representa a la instancia particular del modelo (p. ej. en el sitio de Administracion)
        """
        return self.name

class Language(models.Model):
    """
    Modelo que representa un lenguaje (p. ej. Ingles, frances, japones, etc.).
    """
    name = models.CharField(max_length=200, help_text="Ingrese el lenguaje natural del libro (p. ej. Ingles, frances, japones, etc.).")

    def __str__(self) -> str:
        """
        String que representa al Objeto Modelo
        """
        return self.name

class Book(models.Model):
    """
    Modelo que representa un libro (pero no un Ejemplar especifico).
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # ForeignKey, ya que un libro tiene un solo autor, pero el mismo autor puede haber escrito muchos libros.
    # 'Author' es un string, en vez de un objeto, porque la clase Author aun no ha sido declarada.
    
    summary = models.TextField(max_length=1000, help_text="Ingrese una breve descripcion del libro")
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Caracteres <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Seleccione un genero para este libro")
    # ManyToManyField, porque un genero puede contener muchos libros y un libro puede cubrir varios generos.
    # La clase Genre ya ha sido definida, entonces podemos especificar el objeto arriba.
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def display_genre(self):
        """
        Crea un string para el genero. Esto es requerido para mostrar el genero en admin
        """
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    
    display_genre.short_description = 'Genre'

    def __str__(self) -> str:
        """
        String que representa al objeto book
        """
        return self.title
    
    def get_absolute_url(self):
        """
        Devuelve el URL a una instancia particular de Book
        """
        return reverse('book-detail', args=[str(self.id)])

class BookInstance(models.Model):
    """
    Modelo que representa una copia especifica de un libro (i.e. que puede ser prestado por la biblioteca).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="ID unico para este libro particular en toda la biblioteca")
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved')
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Disponibilidad del libro')

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"), )
    
    def __str__(self) -> str:
        """
        String para representar el Objeto del Modelo
        """
        return '{0} ({1})'.format(self.id, self.book.title)
    
    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

class Author(models.Model):
    """
    Modelo que representa un autor
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
        """
        Retorna la url para acceder a una instancia particular de un autor.
        """
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self) -> str:
        """
        String que representa el Objeto Modelo
        """
        return '{0}, {1}'.format(self.last_name, self.first_name)

    class Meta:
        ordering = ["last_name"]
        permissions = (("create_author", "Can create a new author"), )