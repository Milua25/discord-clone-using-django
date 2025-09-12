from rest_framework import status
from rest_framework.decorators import  api_view
from rest_framework.response import Response
from .serializers import RoomSerializer
from ..models import Room


@api_view(['GET'])
def getRoutes(request):
    routes = [
        "GET /api"
        "GET /api/rooms",
        "GET /api/rooms/<room_id>",
    ]
    return Response(routes)


@api_view(['GET'])
def get_rooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_room(request,pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        serializer = RoomSerializer(room, many=False)
        return Response(serializer.data)