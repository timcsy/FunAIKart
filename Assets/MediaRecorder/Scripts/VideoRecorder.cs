using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

public struct VideoFrame
{
    public Texture2D texture;
    public TimeSpan timestamp;
    public VideoFrame(Texture2D texture, TimeSpan timestamp)
    {
        this.texture = texture;
        this.timestamp = timestamp;
    }
}

public struct AudioFrame
{
    public float[] data;
    public int channels;
    public TimeSpan timestamp;
    public AudioFrame(float[] data, int channels, TimeSpan timestamp)
    {
        this.data = data;
        this.channels = channels;
        this.timestamp = timestamp;
    }
}

public class VideoRecorder : MonoBehaviour
{
    // Static instance and variables
    public static VideoRecorder instance; // One can access the VideoRecorder instance outside the class
    
    [SerializeField, Tooltip("negative means using the original size with scaling")]
    private int videoWidth = -1;
    [SerializeField, Tooltip("negative means using the original size with scaling")]
    private int videoHeight = -1;
    [SerializeField]
    private int depth = 0;

    private List<VideoFrame> videoFrames;
    private List<AudioFrame> audioFrames;
    private int sampleRate;
    DateTime startTime;
    private bool isRecording = false;
    private bool isPaused = true;

    // Awake is called before Start(), whether or not the script is enabled
    private void Awake()
    {
        Resize(false);
        // Assign the static instance
        if (!instance) { 
            instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else Destroy(gameObject); // Maintain singleton property 
        // (for some reasons, without this, there may be two Main Cameras with DontDestroyOnLoad after reloading)
    }

    public void Begin()
    {
        isRecording = true;
        isPaused = false;
        startTime = DateTime.Now;
        StartCoroutine(CaptureUI());
    }

    public void End()
    {
        isPaused = true;
        isRecording = false;
    }

    public void Pause()
    {
        isPaused = true;
    }

    public void Resume()
    {
        isPaused = false;
    }

    public void UpdateAudio(float[] data, int channels)
    {
        if (isRecording && !isPaused)
        {
            float[] buffer = new float[data.Length];
            data.CopyTo(buffer, 0);
            var audioFrame = new AudioFrame(buffer, channels, DateTime.Now - startTime);
            audioFrames.Add(audioFrame);
        }
    }

    // Start is called before the first frame update
    void Start()
    {
        videoFrames = new List<VideoFrame>();
        audioFrames = new List<AudioFrame>();
        sampleRate = AudioSettings.outputSampleRate;
        string config_file = "Records/config.txt";
        if (File.Exists(config_file)) instance.Begin();
    }

    public void Resize(bool fullscreen=false)
    {
        string config_file = "Screen.config";
        if (File.Exists(config_file))
        {
            // Dealing with path to save images and audio
            string size = File.ReadAllText(config_file).Trim();
            var sizes = size.Split('x');
            if (sizes.Length == 2)
            {
                int width = -1;
                bool has_width = int.TryParse(sizes[0], out width);
                int height = -1;
                bool has_height = int.TryParse(sizes[1], out height);
                if (has_width && has_height && width >= 0 && height >= 0)
                {
                    Screen.SetResolution(width, height, fullscreen);
                }
            }
        }
    }

    private IEnumerator CaptureUI()
    {
        while (isRecording)
        {
            // Capture just after frame update rendering, otherwise you will get something else
            yield return new WaitForEndOfFrame();

            if (!isPaused)
            {
                var m_screenTexture = new RenderTexture(Screen.width, Screen.height, depth);
                ScreenCapture.CaptureScreenshotIntoRenderTexture(m_screenTexture);
                var output_width = (videoWidth < 0)? (int)Mathf.Floor(-Screen.width * videoWidth): videoWidth;
                var output_height = (videoHeight < 0)? (int)Mathf.Floor(-Screen.height * videoHeight): videoHeight;
                Texture2D tex;
                if (Screen.width == output_width && Screen.height == output_height)
                {
                    tex = toTexture2D(m_screenTexture);
                }
                else
                {
                    var m_outputTexture = new RenderTexture(output_width, output_height, depth);
                    Graphics.Blit(m_screenTexture, m_outputTexture);
                    tex = toTexture2D(m_outputTexture);
                }
                var videoFrame = new VideoFrame(tex, DateTime.Now - startTime);
                videoFrames.Add(videoFrame);
            }
        }
    }

    private Texture2D toTexture2D(RenderTexture rt)
    {
        var oldRT = RenderTexture.active;

        var tex = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);
        RenderTexture.active = rt;
        tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
        tex.Apply();

        RenderTexture.active = oldRT;

        return tex;
    }
    private Texture2D FlipTexture(Texture2D tex)
    {
        // upside-down
        Texture2D snap = new Texture2D(tex.width, tex.height, TextureFormat.RGB24, false);
        Color[] pixels = tex.GetPixels();
        Color[] pixelsFlipped = new Color[pixels.Length];

        for (int i = 0; i < tex.height; i++)
        {
            Array.Copy(pixels, i * tex.width, pixelsFlipped, (tex.height - i - 1) * tex.width, tex.width);
        }

        snap.SetPixels(pixelsFlipped);
        snap.Apply();
        return snap;
    }
    private void SaveImages(String path, String filename)
    {
        int numFrames = videoFrames.Count;
        // Check if the environment need to flip upside-down
        var flipY = SystemInfo.graphicsDeviceType == GraphicsDeviceType.OpenGLCore ||
                    SystemInfo.graphicsDeviceType == GraphicsDeviceType.OpenGLES2 ||
                    SystemInfo.graphicsDeviceType == GraphicsDeviceType.OpenGLES3 ||
                    SystemInfo.graphicsDeviceType == GraphicsDeviceType.Vulkan ?
                    false: true;
        // Make sure directory exists if user is saving to sub dir.
        Directory.CreateDirectory(path);
        using (var fileStream = new FileStream(path + "/" + filename + ".txt", FileMode.Create))
        using (var writer = new StreamWriter(fileStream))
        {
            String fullName = null;
            for (int i = 0; i < numFrames; i++)
            {
                Texture2D tex;
                if (flipY) tex = FlipTexture(videoFrames[i].texture);
                else tex = videoFrames[i].texture;
                byte[] buffer = tex.EncodeToPNG();
                if (fullName != null)
                {
                    TimeSpan diff = videoFrames[i].timestamp - videoFrames[i-1].timestamp;
                    writer.WriteLine("duration {0}", diff.TotalSeconds);
                }
                fullName = filename + "_" + i + ".png";
                File.WriteAllBytes(path + "/" + fullName, buffer);
                writer.WriteLine("file '{0}'", fullName);
            }
        }
    }

    private void SaveAudio(String path, String filename)
    {
        int numFrames = audioFrames.Count;
        int channels = 0;
        for (int i = 0; i < numFrames; i++)
        {
            if (audioFrames[i].channels > channels) channels = audioFrames[i].channels;
        }
        int numSamples = 0;
        for (int i = 0; i < numFrames; i++)
        {
            numSamples += audioFrames[i].data.Length / audioFrames[i].channels;
        }
        float[] buffer = new float[channels * numSamples];
        int offset = 0;
        for (int n = 0; n < numFrames; n++)
        {
            for (int i = 0; i < audioFrames[n].data.Length; i++)
            {
                int s = i / audioFrames[n].channels;
                int c = i % audioFrames[n].channels;
                buffer[(offset + s) * channels + c] = audioFrames[n].data[i];
            }
            offset += audioFrames[n].data.Length / audioFrames[n].channels;
        }
        AudioClip clip = AudioClip.Create("Audio", numSamples, channels, sampleRate, false);
        clip.SetData(buffer, 0);
        // Make sure directory exists if user is saving to sub dir.
        Directory.CreateDirectory(path);
        SavWav.Save(path + "/" + filename + ".wav", clip);
    }

    public void CleanMemory()
    {
        int identificador = GC.GetGeneration(videoFrames);
        videoFrames.Clear();
        GC.Collect(identificador, GCCollectionMode.Forced);
        identificador = GC.GetGeneration(audioFrames);
        videoFrames.Clear();
        GC.Collect(identificador, GCCollectionMode.Forced);
    }

    public void SaveAll()
    {
        string config_file = "Records.config";
        if (File.Exists(config_file))
        {
            // Dealing with path to save images and audio
            string path = File.ReadAllText(config_file).Trim();
            if (path == "")
            {
                path = "Records/" + System.DateTime.Now.ToString("yyyyMMddHHmmss");
            }
            path = Path.GetFullPath(path);
            Directory.CreateDirectory(path);

            // output video size
            var output_width = (videoWidth < 0)? (int)Mathf.Floor(-Screen.width * videoWidth): videoWidth;
            var output_height = (videoHeight < 0)? (int)Mathf.Floor(-Screen.height * videoHeight): videoHeight;
            string size = "" + output_width + "x" + output_height;
            using (StreamWriter outputFile = new StreamWriter(Path.Combine(path, "size.txt"), true))
            {
                outputFile.WriteLine(size);
            }

            SaveImages(path, "img");
            SaveAudio(path, "audio"); // The Audio can indicate the length of the video
            CleanMemory();
        }
    }

    void OnApplicationQuit()
    {
        #if !UNITY_EDITOR
        SaveAll();
        #endif
    }

    void OnDestroy()
    {
        #if UNITY_EDITOR
        SaveAll();
        #endif
    }
}