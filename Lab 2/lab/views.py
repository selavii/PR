from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Product, UploadedFile
from .serializers import ProductSerializer, FileUploadSerializer


class CreateProductView(generics.CreateAPIView):
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            product = serializer.save()
            return Response({'message': 'Product created!'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Error creating the product!'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteProductView(generics.DestroyAPIView):
    serializer_class = ProductSerializer

    def delete(self, request):
        product_id = request.query_params['product_id']

        try:
            Product.objects.get(id=product_id).delete()
            return Response({'message': 'Product deleted successfully!'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'message': 'This user did not create this product!'}, status=status.HTTP_404_NOT_FOUND)


class GetProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all()


class GetProductView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer

    def get_object(self):
        product_id = self.request.query_params.get('product_id')
        return Product.objects.get(id=product_id)


class UpdateProductView(generics.UpdateAPIView):
    serializer_class = ProductSerializer

    def get_object(self):
        product_id = self.request.query_params['product_id']
        return Product.objects.get(id=product_id)


class FileUploadView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'File uploaded successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.http import JsonResponse

def index(request):
    return JsonResponse({"message": "Welcome to the chat server!"})
