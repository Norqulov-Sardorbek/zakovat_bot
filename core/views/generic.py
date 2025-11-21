from django.contrib.contenttypes.models import ContentType
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotAcceptable
from rest_framework.viewsets import ModelViewSet


class GenericModelViewSet(ModelViewSet):
    model_mapping = {}

    model_name = openapi.Parameter(
        "model_name",
        openapi.IN_QUERY,
        description="Model name",
        type=openapi.TYPE_STRING,
    )
    object_id = openapi.Parameter(
        "object_id",
        openapi.IN_QUERY,
        description="Object id",
        type=openapi.TYPE_INTEGER,
    )

    def get_queryset(self):
        if self.action == "list":
            model_name = self.request.query_params.get("model_name")
            object_id = self.request.query_params.get("object_id")
            model = self._get_model(model_name)
            content_type = ContentType.objects.get_for_model(model)
            return self.queryset.filter(content_type=content_type, object_id=object_id)
        return super().get_queryset()

    @swagger_auto_schema(manual_parameters=[model_name, object_id])
    def list(self, request, *args, **kwargs):
        self._validate_query_params(request)
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[model_name, object_id])
    def create(self, request, *args, **kwargs):
        self._validate_query_params(request)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        model, model_name, object_id = self._validate_query_params(self.request)
        serializer.save(content_type=ContentType.objects.get_for_model(model), object_id=object_id)

    def _get_model(self, model_name):
        model = self.model_mapping.get(model_name)
        if not model:
            raise NotAcceptable(
                {"message": f"Invalid model_name: {model_name}"},
                code=status.HTTP_400_BAD_REQUEST,
            )
        return model

    def _validate_query_params(self, request, object_id_required=False):
        model_name = request.query_params.get("model_name")
        object_id = request.query_params.get("object_id")
        if not model_name:
            raise NotAcceptable(
                {"message": "model_name query param is required"},
                code=status.HTTP_400_BAD_REQUEST,
            )
        if object_id_required and not object_id:
            raise NotAcceptable(
                {"message": "object_id query param is required"},
                code=status.HTTP_400_BAD_REQUEST,
            )
        model = self._get_model(model_name)
        return model, model_name, object_id
