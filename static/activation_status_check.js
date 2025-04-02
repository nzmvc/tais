document.addEventListener('DOMContentLoaded', function () {
    const activationMessage = document.getElementById('activation-message');

    // Aktivasyon durumunu kontrol eden fonksiyon
    function checkActivationStatus() {
        fetch('/api/check-activation-status/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'), // CSRF koruması için
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.is_active) {
                    // Kullanıcı aktifse, mesajı güncelle ve sayfayı yönlendir
                    activationMessage.innerHTML = "<p>Hesabınız aktif hale getirildi. Yönlendiriliyorsunuz...</p>";
                    setTimeout(() => {
                        window.location.href = '/';  // Ana sayfaya yönlendir
                    }, 2000);
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Her 5 saniyede bir aktivasyon durumunu kontrol et
    setInterval(checkActivationStatus, 5000);

    // CSRF token'ı almak için fonksiyon
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
