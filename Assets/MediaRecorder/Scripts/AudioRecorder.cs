using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[RequireComponent(typeof(AudioListener))]
public class AudioRecorder : MonoBehaviour
{
    private void OnAudioFilterRead(float[] data, int channels)
    {
        // VideoRecorder.instance.UpdateAudio(data, channels);
    }
}
