public class BananaPickUp : PickUpClass
{
    public override void PickUpEffect(PAIAKartAgent kart)
    {
        PickUpManager.instance.PickUp(PickUpType.Banana, kart);
    }
}