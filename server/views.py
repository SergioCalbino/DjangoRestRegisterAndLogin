from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authentication import TokenAuthentication 
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

@api_view(['POST'])
def login(request):

    # Primero busco si el usuario existe en la db. Busco dentro del modelo User y le indico por cual campo
    user = get_object_or_404(User, username=request.data['username'])
    
    # valido si la contraseña ingresada es la correcta
    if not user.check_password(request.data['password']):
        return Response({'error': 'Usuario o contraseña incorrecta'},status=status.HTTP_400_BAD_REQUEST)
    
    token, created = Token.objects.get_or_create(user=user)
    # Ahora serializo los datos de python en diccionario, lo paso a json
    serializer = UserSerializer(instance=user)
    print(serializer)
    
    return Response({"token": token.key, "user": serializer.data} )
    

@api_view(['POST'])
def register(request):
    # para el register debo validar con el Userserializar los datoss que me llegan ppr body con el requeset.data
    serializer = UserSerializer(data=request.data)
    
    # Esto valida que los datos enviados son correctos
    if serializer.is_valid():
        serializer.save()
        
        # si estan correctos los datos, creo un nuevo modelo de usuario en la base de datos
        # y lo devuelvo como respuesta
        
        user = User.objects.get(username=serializer.data['username'])
        user.set_password(serializer.data['password'])
        user.save()
        
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
# De este forma indico que en el header tiene que tener una autenticacion para poder acceder
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    
    serializer = UserSerializer(instance=request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
    # return Response('Estas logueado con {}'.format(request.user.username), status=status.HTTP_200_OK)



