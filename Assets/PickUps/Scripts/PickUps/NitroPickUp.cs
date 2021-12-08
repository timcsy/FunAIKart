public class NitroPickUp : PickUpClass
{
    public override void PickUpEffect(PAIAKartAgent kart)
    {
        PickUpManager.instance.PickUp(PickUpType.Nitro, kart);
    }
}