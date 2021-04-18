# Generated by Django 3.1.4 on 2021-04-03 05:20

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clases', '0001_initial'),
        ('usuarios', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Foro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120)),
                ('descripcion', models.TextField()),
                ('estado', models.CharField(choices=[('Abierto', 'Abierto'), ('Cerrado', 'Cerrado'), ('Por abrir', 'Por abrir')], default='Abierto', max_length=9)),
                ('fecha_de_inicio', models.DateTimeField()),
                ('fecha_de_cierre', models.DateTimeField()),
                ('fecha_de_creacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('eliminado', models.BooleanField(default=False)),
                ('clase', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='clases.clase')),
            ],
        ),
        migrations.CreateModel(
            name='Participacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('participacion', models.TextField()),
                ('eliminada', models.BooleanField(default=False)),
                ('foro', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='foros.foro')),
                ('participante', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='usuarios.persona')),
            ],
        ),
        migrations.CreateModel(
            name='Respuesta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_respuesta', models.IntegerField()),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('respuesta', models.TextField()),
                ('eliminada', models.BooleanField(default=False)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='usuarios.persona')),
                ('participacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foros.participacion')),
            ],
        ),
        migrations.AddField(
            model_name='foro',
            name='participaciones',
            field=models.ManyToManyField(through='foros.Participacion', to='usuarios.Persona'),
        ),
    ]