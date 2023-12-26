using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ScaleCube : MonoBehaviour
{
    public float scale;
   public void Scale(float value) {
       scale = value/120;
   }

   private void Update() {
    transform.localScale = new Vector3(scale, 1, 1);
   }
}