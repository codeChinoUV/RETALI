from django.shortcuts import redirect


class MaestroMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.es_maestro:
            return super().dispatch(request, *args, **kwargs)
        return redirect('inicio')


class AlumnoMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.es_maestro:
            return super().dispatch(request, *args, **kwargs)
        return redirect('inicio')