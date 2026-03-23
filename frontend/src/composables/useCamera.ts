import { ref, onUnmounted } from 'vue'

export function useCamera() {
  const videoRef = ref<HTMLVideoElement | null>(null)
  const stream = ref<MediaStream | null>(null)
  const error = ref<string | null>(null)
  const isActive = ref(false)

  async function startCamera() {
    try {
      error.value = null
      stream.value = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1920 },
          height: { ideal: 1080 },
          facingMode: 'user'
        },
        audio: false
      })
      
      if (videoRef.value) {
        videoRef.value.srcObject = stream.value
        await videoRef.value.play()
        isActive.value = true
      }
    } catch (err) {
      error.value = 'Kamera tidak terdeteksi'
      console.error('Camera error:', err)
    }
  }

  function stopCamera() {
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop())
      stream.value = null
      isActive.value = false
    }
  }

  function capturePhoto(): Blob | null {
    if (!videoRef.value || !isActive.value) return null

    const canvas = document.createElement('canvas')
    canvas.width = videoRef.value.videoWidth
    canvas.height = videoRef.value.videoHeight
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return null

    ctx.drawImage(videoRef.value, 0, 0)
    
    return new Promise<Blob | null>((resolve) => {
      canvas.toBlob((blob) => {
        resolve(blob)
      }, 'image/jpeg', 0.95)
    }) as unknown as Blob
  }

  async function capturePhotoAsync(): Promise<Blob | null> {
    return capturePhoto()
  }

  onUnmounted(() => {
    stopCamera()
  })

  return {
    videoRef,
    stream,
    error,
    isActive,
    startCamera,
    stopCamera,
    capturePhoto,
    capturePhotoAsync
  }
}
