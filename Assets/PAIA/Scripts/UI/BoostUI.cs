using UnityEngine;

public class BoostUI : MonoBehaviour
{
    [SerializeField]
    private UnityEngine.UI.Image progressBar;
    [SerializeField]
    private UnityEngine.UI.Text title;

    private float duration = -1;
    private float startTime = -1;

    public void Initialize(float dur, Color effectColor, string effectTitle)
    {
        startTime = Time.time;
        duration = dur;

        progressBar.color = effectColor;
        title.text = effectTitle;
    }

    void Update()
    {
        if (Time.time - startTime >= duration)
        {
            Destroy(gameObject);
        }
        progressBar.fillAmount = 1 - ((Time.time - startTime) / duration);
    }
}