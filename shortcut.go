package main

import (
	"fmt"
	"log"
	"os/exec"
	"syscall"

	"golang.design/x/hotkey"
	"golang.design/x/hotkey/mainthread"
)

func main() {
	mainthread.Init(func() {
		hk := hotkey.New([]hotkey.Modifier{hotkey.ModCtrl, hotkey.ModShift}, hotkey.KeyH)

		if err := hk.Register(); err != nil {
			log.Fatalf("failed to register hotkey: %v", err)
		}
		defer hk.Unregister()

		fmt.Println("Listening for Ctrl+Shift+H...")
		fmt.Println("Press Ctrl+C to exit")

		for {
			<-hk.Keydown()
			fmt.Println("hello")
			
			// Configuration pour lancer Python sans console
			cmd := exec.Command("pythonw", "main.py")
			cmd.SysProcAttr = &syscall.SysProcAttr{
				HideWindow: true,
			}
			
			err := cmd.Start()
			if err != nil {
				log.Println("Failed to run script:", err)
			}
		}
	})
}
