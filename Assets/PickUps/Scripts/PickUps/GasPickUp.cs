public class GasPickUp : PickUpClass
{
    public override void PickUpEffect(PAIAKartAgent kart)
    {
        PickUpManager.instance.PickUp(PickUpType.Gas, kart);
    }
}