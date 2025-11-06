from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, ProductSerializer, OrderSerializer, DeliveryAddressSerializer, CategorySerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import Product, Order, DeliveryAddress, Category
from rest_framework.serializers import ModelSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend

class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key})
            return Response({"error": "Invalid credentials"}, status=400)
        return Response(serializer.errors, status=400)
        
class IsAdminUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # GET
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # POST/PUT/DELETE — is_staff
        return request.user and request.user.is_staff      
  
        
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = ProductFilter
    search_fields = ['title', 'company']
    ordering_fields = ['new_price', 'rating']
    filterset_fields = ['category__name', 'new_price']
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'id'

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


def get_queryset(self):
    queryset = Product.objects.all()
    search = self.request.query_params.get('search')
    ordering = self.request.query_params.get('ordering')
    category = self.request.query_params.get('category')
    price_min = self.request.query_params.get('price_min')
    price_max = self.request.query_params.get('price_max')

    if search:
        queryset = queryset.filter(title__icontains=search)
    if category:
        queryset = queryset.filter(category__name__icontains=category)
    if price_min:
        queryset = queryset.filter(new_price__gte=price_min)
    if price_max:
        queryset = queryset.filter(new_price__lte=price_max)
    if ordering:
        queryset = queryset.order_by(ordering)

    return queryset

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    # 1. Зберігаємо адресу
    address_data = {
        "address": request.data.get("address"),
        "city": request.data.get("city"),
        "postal_code": request.data.get("postal_code"),
        "phone": request.data.get("phone"),
    }
    address, created = DeliveryAddress.objects.update_or_create(
        user=request.user, defaults=address_data
    )

    # 2. Створюємо замовлення
    serializer = OrderSerializer(data={"items": request.data.get("items")}, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response({"success": "Order created!"})
    return Response(serializer.errors, status=400)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_role(request):
    return Response({
        "username": request.user.username,
        "is_staff": request.user.is_staff
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    orders_count = Order.objects.filter(user=user).count()

    return Response({
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "date_joined": user.date_joined,
        "orders_count": orders_count,
    })

def home(request):
    return JsonResponse({'message': 'API is working'})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def delivery_address_view(request):
    try:
        address = DeliveryAddress.objects.get(user=request.user)
    except DeliveryAddress.DoesNotExist:
        address = None

    if request.method == 'GET':
        serializer = DeliveryAddressSerializer(address)
        return Response(serializer.data if address else {})

    elif request.method == 'POST':
        if address:
            serializer = DeliveryAddressSerializer(address, data=request.data)
        else:
            serializer = DeliveryAddressSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)