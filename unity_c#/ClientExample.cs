using System.Collections;
using System;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using Cysharp.Threading.Tasks;
using OscJack;

public class ClientExample : MonoBehaviour
{
    void Start(){
        
    }
    static string serverip = "127.0.0.1";
    OscClient client = new OscClient(serverip, 8067);
    OscClient send_to_python = new OscClient(serverip, 9067);

    async void Update() {
       if (Input.GetKeyDown(KeyCode.S)) {
           Debug.Log("Send to unity");
           client.Send("/osc_B", "Success! by unityA");
       }
       
       if (Input.GetKeyDown(KeyCode.A)) {
           Debug.Log("controll motor");
           send_to_python.Send("/motorA", "fwd.8");
           await UniTask.Delay(TimeSpan.FromSeconds(5));
           send_to_python.Send("/motorA", "stp.00");
           Debug.Log("done");
       }
       if (Input.GetKeyDown(KeyCode.B)) {
           Debug.Log("controll motor");
           send_to_python.Send("/motorB", "rev.8");
           await UniTask.Delay(TimeSpan.FromSeconds(5));
           send_to_python.Send("/motorB", "stp.00");
           Debug.Log("done");
       }
    }

   private void OnDestroy() {
       client.Dispose();
   }
}