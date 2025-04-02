from gorevler.models import Gorevler
from rest_framework import serializers


class GorevlerSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, max_length=190)
    description = serializers.EmailField(required=True, max_length=190)
    statu = serializers.CharField(required=True, max_length=190)
    id = serializers.IntegerField(required=False)
    deadline = serializers.DateTimeField(required=True)
    start_date = serializers.DateTimeField(required=True)
    responsible_user_id = serializers.IntegerField(required=True)


class GorevlerModalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gorevler
        fields = ['id','title', 'description', 'statu','deadline','start_date','responsible_user']

class GorevlerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gorevler
        fields = ['id','title', 'description', 'statu','deadline','start_date','responsible_user']

    # save , create ve update işlemleri için ayrı ayrı tanımlamalar yapılabilir. override edilebilir.
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.statu = validated_data.get('statu', instance.statu)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.responsible_user = validated_data.get('responsible_user', instance.responsible_user)
        instance.save()
        return instance
    
    def validate_title(self, value):        # update işleminde bir kontrol yapılabilir. title 10 karakterden az olamaz gibi. Bu sadece title için yapılır.
        if len(value) < 10:
            raise serializers.ValidationError("Başlık 10 karakterden az olamaz.")
        return value
    def validate(self, attrs):
        print(attrs)        # tüm alanlar için bir kontrol yapılabilir. örneğin title ve description aynı olamaz gibi.
        if attrs['title'] == attrs['description']:
            raise serializers.ValidationError("Başlık ve açıklama aynı olamaz.")
        if attrs['start_date'] > attrs['deadline']:
            raise serializers.ValidationError("Başlangıç tarihi bitiş tarihinden büyük olamaz.")
        
        return super().validate(attrs)


    def create(self, validated_data):
        return Gorevler.objects.create(**validated_data)
    
    def save(self, **kwargs):
        return super().save(**kwargs)