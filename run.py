from controller.main import GameController
import util

def main():
    util.clear_log()
    controller = GameController()
    controller.run()

if __name__ == "__main__":
    main()
