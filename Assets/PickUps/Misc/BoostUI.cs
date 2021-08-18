using UnityEngine;

public class BoostUI : MonoBehaviour
{
    [SerializeField]
    private UnityEngine.UI.Image progressBar;

    private float duration = -1;
    private float startTime = -1;

    public void SetDuration(float dur)
    {
        startTime = Time.time;
        duration = dur;
    }

    void Update()
    {
        if (Time.time - startTime >= duration)
            Destroy(gameObject);
        progressBar.fillAmount = 1 - ((Time.time - startTime) / duration);
    }
}