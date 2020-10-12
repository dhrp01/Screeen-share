import socket
import pygame
import zlib

WIDTH = 1920
HEIGHT = 1080


def recvall(conn, size):
    """
    Function to receive complete image data
    """
    buf = b''
    while len(buf) < size:
        data = conn.recv(1024)
        if not data:
            return data
        buf += data
    return buf


if __name__ == '__main__':
    pygame.init()
    screen_info = pygame.display.Info()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    watching = True
    connected = False
    soc = socket.socket()

    # wait for the publisher to get connected
    while not connected:
        try:
            soc.connect(('192.168.0.100', 5000))
            connected = True
        except Exception as e:
            print('presenter is not here will try again')

    try:
        while watching:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    watching = False
                    break
            size_len = int.from_bytes(soc.recv(1), byteorder='big')
            size = int.from_bytes(soc.recv(size_len), byteorder='big')
            pixel = zlib.decompress(recvall(soc, size))

            img = pygame.image.fromstring(pixel, (WIDTH, HEIGHT), 'RGB')
            img = pygame.transform.scale(img, (screen_info.current_w, screen_info.current_h))
            screen.blit(img, (0,0))
            pygame.display.flip()
            clock.tick(60)
    finally:
        soc.close()
