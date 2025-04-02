from django.shortcuts import render
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User,Permission,Group
from gorevler.models import Gorevler,GorevlerStatu,GorevNotu
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from api.serializers import GorevlerSerializer,GorevlerModalSerializer,GorevlerUpdateSerializer
from rest_framework.generics import ListAPIView,RetrieveAPIView,DestroyAPIView,UpdateAPIView,CreateAPIView,RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin, RetrieveModelMixin
from api.paginations import CustomPagination
from api.permissions import IsOwner


class GorevlerView(ListAPIView):
    #queryset = Gorevler.objects.all()      # queryset tanımlanmazsa get_queryset fonksiyonu çalışır.burada tüm veriler alınıyor
    serializer_class = GorevlerModalSerializer
    permission_classes = [IsAuthenticated]  # kullanıcı yetkisi kontrol edilir. is authenticated permission classı kullanılır.
    """search_fields = ['title']
    ordering_fields = ['id','title','description','statu','deadline','start_date','responsible_user']"""
    pagination_class = CustomPagination  # pagination yapısı tanımlanabilir. custom pagination classı oluşturulur.

    def get_queryset(self):     # queryset tanımlanmazsa get_queryset fonksiyonu çalışır.burada tüm veriler alınıyor
        return Gorevler.objects.filter(open_user=self.request.user)  # kullanıcının açtığı görevler listelenir.
    
    filter_backends = [SearchFilter,OrderingFilter]  # arama ve sıralama yapılacak alanlar . link olarak ordering=title  dersek title a göre sıralar
    search_fields = ['title']  # arama yapılacak alanlar birden fazla olabilir.

    #http://localhost:8000/api/gorevler?search=a&ordering=title         -title denirse tersten sıralar

class GorevlerDeatilView(RetrieveAPIView):
    queryset = Gorevler.objects.all() 
    serializer_class = GorevlerModalSerializer
    lookup_field = 'id'




# hem update hem delete işlemini aynı yerde yapabiliyoruz. deleteApıview e ihtiyacımız kalmadı
class GorevlerUpdateView(RetrieveUpdateAPIView,DestroyModelMixin,UpdateModelMixin):        #!!!! updateAPIView ile RetrieveUpdateAPIView farkı nedir? retrieveupdateapiview hem get hemde put işlemlerini yapar. yani hem veriyi getirir hemde günceller.
    queryset = Gorevler.objects.all()                                           #destroyModelMixin ile destroy işlemi yapılır. updateModelMixin ile update işlemi yapılır.
    serializer_class = GorevlerUpdateSerializer         
    lookup_field = 'id'
    permission_classes = [IsOwner]  # kullanıcı yetkisi kontrol edilir. gorevin sahibi olmalı. is owner permission classı kullanılır.bunu biz tanımladık.

    def perform_update(self, serializer):
        serializer.save(open_user=self.request.user)    # kayıt güncellendikten sonra yapılacak işlemler. güncellene tarih yada güncelleyen kullanıcı otomatik girilebilir.

    def delete(self,request,*args,**kwargs):            # 
        return self.destroy(request,*args,**kwargs)

class GorevlerCreateView(CreateAPIView):
    queryset = Gorevler.objects.all() 
    serializer_class = GorevlerModalSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated,IsAdminUser]  # kullanıcı yetkisi kontrol edilir.iki kosulda sağlanmalı. VE olarak düşün

    def perform_create(self, serializer):           # kayıt oluşturulduktan sonra yapılacak işlemler
        serializer.save(open_user=self.request.user)
        #send_mail( 'Görev Oluşturuldu','Görev Oluşturuldu','   ', ['  '],   fail_silently=False, )  # mail gonderimi de yapılabilir
        #send_sms    sms de gonderebiliriz.


class GorevlerDeleteView(DestroyAPIView, UpdateModelMixin, RetrieveModelMixin):   # mixin leri kullanarak detele işlemine ek olarak update ve get işlemleri de yapılabilir.
    queryset = Gorevler.objects.all() 
    serializer_class = GorevlerModalSerializer
    lookup_field = 'id'
    permission_classes = [IsOwner]  # kullanıcı yetkisi kontrol edilir. gorevin sahibi olmalı. is owner permission classı kullanılır.bunu biz tanımladık.

    def put (self,request,*args,**kwargs):
        return self.update(request,*args,**kwargs)
    def get (self,request,*args,**kwargs):
        return self.retrieve(request,*args,**kwargs)

@csrf_exempt
def check_activation_status(request):
    """user = request.user
    is_active = user.is_active  # Kullanıcının aktiflik durumu
    return JsonResponse({'is_active': is_active})"""
    print("check_activation_status")
    if request.method == 'POST':
        # JSON verisini al
        import json
        data = json.loads(request.body)
        phone_number = data.get('phone_number')  # Telefon numarasını al
        print("phone:",phone_number)
        # Kullanıcıyı telefon numarasına göre sorgula
        try:
            user = User.objects.get(username=phone_number)  # Örnek: Telefon numarası profile modelinde
            
            if user.is_active:
                print("user is active, login komut çalışacak")
                login(request, user)
            
            is_active = user.is_active  # Kullanıcının aktiflik durumu
            print("is_active:",is_active)
            return JsonResponse({'is_active': is_active})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)