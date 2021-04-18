# Generated by Django 3.1.4 on 2021-04-03 05:18

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clases', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField()),
                ('fecha_de_inicio', models.DateTimeField()),
                ('fecha_de_cierre', models.DateTimeField()),
                ('nombre', models.CharField(max_length=120)),
                ('estado', models.CharField(choices=[('Abierta', 'Abierta'), ('Cerrada', 'Cerrada'), ('Por abrir', 'Por abrir')], default='Por abrir', max_length=9)),
                ('fecha_de_creacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('clase', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='clases.clase')),
            ],
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calificacion', models.FloatField()),
                ('retroalimentacion', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Entrega',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentarios', models.TextField(null=True)),
                ('fecha_de_entrega', models.DateTimeField(default=django.utils.timezone.now)),
                ('actvidad', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='actividades.actividad')),
                ('alumno', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='clases.alumno')),
                ('revision', models.OneToOneField(null=True, on_delete=django.db.models.deletion.RESTRICT, to='actividades.revision')),
            ],
        ),
        migrations.CreateModel(
            name='Archivo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(upload_to='entregas')),
                ('entrega', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='actividades.entrega')),
            ],
        ),
        migrations.AddField(
            model_name='actividad',
            name='entregas',
            field=models.ManyToManyField(through='actividades.Entrega', to='clases.Alumno'),
        ),
    ]
