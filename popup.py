import dearpygui.dearpygui as dpg
import time
import threading
import uuid

class NotificationManager:
    def __init__(self):
         
        self.active_notifications = []
        self.notification_lock = threading.Lock()

    def show_notification(self, text, duration=3.0, raison="warning"):
        """
        Affiche une notification popup en bas à droite de l'écran avec une animation de type slide.
        Les notifications s'empilent verticalement quand plusieurs sont affichées simultanément.
        
        Args:
            text (str): Le texte à afficher dans la notification
            duration (float): La durée d'affichage en secondes
        """
        
        # Générer un identifiant unique pour cette notification
        notif_id = f"notification_{str(uuid.uuid4())[:8]}"
        
        # Obtenir les dimensions du viewport
        viewport_width = dpg.get_viewport_width()
        viewport_height = dpg.get_viewport_height()
        
        # Dimensions de la notification
        notif_width = 300
        notif_height = 100
        
        # Position initiale pour l'animation (hors écran)
        start_x = viewport_width
        
        # Calculer la position verticale en fonction des notifications déjà affichées
        with self.notification_lock:
            # Chaque nouvelle notification apparaît sous les précédentes
            notif_count = len(self.active_notifications)
            final_y = viewport_height - notif_height - 30 - (notif_count * (notif_height + 20))
            
            # Position finale (en bas à droite)
            final_x = viewport_width - notif_width - 20
            
            # Ajouter cette notification au registre
            self.active_notifications.append({
                "id": notif_id,
                "y": final_y,
                "height": notif_height
            })
        
        # Créer la fenêtre de notification
        with dpg.window(label="Notification", tag=notif_id, 
                    width=notif_width, height=notif_height, 
                    pos=[start_x, final_y],
                    no_title_bar=True, no_resize=True, no_move=True,
                    no_collapse=True, no_close=True):
            dpg.add_text(text, wrap=notif_width-20)

            if raison == str("warning"): 
                with dpg.theme() as theme:
                        with dpg.theme_component(dpg.mvAll):
                            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [255, 171, 0, 200], category=dpg.mvThemeCat_Core)
                            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5, category=dpg.mvThemeCat_Core)
                            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
                dpg.bind_item_theme(notif_id, theme)
            if raison == str("alert"): 
                with dpg.theme() as theme:
                        with dpg.theme_component(dpg.mvAll):
                            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [231, 76, 60, 200], category=dpg.mvThemeCat_Core)
                            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5, category=dpg.mvThemeCat_Core)
                            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
                dpg.bind_item_theme(notif_id, theme)
            if raison == str("info"): 
                with dpg.theme() as theme:
                        with dpg.theme_component(dpg.mvAll):
                            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [0, 132, 247, 200], category=dpg.mvThemeCat_Core)
                            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5, category=dpg.mvThemeCat_Core)
                            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
                dpg.bind_item_theme(notif_id, theme)
        
        def _animation_thread():
            # Animation d'apparition (slide de droite à gauche)
            steps = 20
            for i in range(steps + 1):
                progress = i / steps
                current_x = start_x - (start_x - final_x) * progress
                dpg.set_item_pos(notif_id, [current_x, final_y])
                time.sleep(0.01)

                
            # Attendre la durée spécifiée
            time.sleep(duration)
            
            # Animation de disparition (slide de gauche à droite)
            for i in range(steps + 1):
                progress = i / steps
                current_x = final_x + (start_x - final_x) * progress
                dpg.set_item_pos(notif_id, [current_x, final_y])
                time.sleep(0.01)
            
            # Supprimer la notification
            dpg.delete_item(notif_id)
            
            # Réorganiser les notifications restantes
            with self.notification_lock:
                # Retirer cette notification du registre
                self.active_notifications[:] = [n for n in self.active_notifications if n["id"] != notif_id]
                
                # Réorganiser les notifications restantes pour combler l'espace
                for i, notif in enumerate(self.active_notifications):
                    new_y = viewport_height - notif["height"] - 20 - (i * (notif["height"] + 10))
                    # Animer le déplacement vers la nouvelle position
                    self._animate_notification_move(notif["id"], notif["y"], new_y)
                    notif["y"] = new_y
        
        # Démarrer l'animation dans un thread séparé pour ne pas bloquer l'interface
        threading.Thread(target=_animation_thread, daemon=True).start()
        #threading.Thread(target=_animation_thread, daemon=True).start()
    def _animate_notification_move(self, notif_id, start_y, end_y):
        if not dpg.does_item_exist(notif_id):
            return
        dpg.focus_item(notif_id)
        current_x = dpg.get_item_pos(notif_id)[0]
        steps = 10
        for i in range(steps + 1):
            progress = i / steps
            current_y = start_y + (end_y - start_y) * progress
            dpg.set_item_pos(notif_id, [current_x, current_y])
            time.sleep(0.01)

if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="Exemple de Notifications Empilées", width=800, height=600)
    notification_manager = NotificationManager()
    with dpg.window(label="Démo", width=780, height=580, id="test"):
        dpg.set_primary_window("test", True)
        dpg.add_text("Cliquez sur les boutons pour afficher des notifications.")
        dpg.add_button(label="Notification courte",  callback=lambda: notification_manager.show_notification("Notification courte!", 3.0, "warning"))
        dpg.add_button(label="alrtt",  callback=lambda: notification_manager.show_notification("Notification courte!", 3.0, "alert"))
        dpg.add_button(label="Info",  callback=lambda: notification_manager.show_notification("Notification courte!", 3.0, "info"))

    dpg.setup_dearpygui()  
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()