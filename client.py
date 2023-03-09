import httpx
import cv2
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str)
    parser.add_argument('stream', type=str)
    args = parser.parse_args()

    try:
        source = int(args.source)
    except ValueError:
        source = args.source
    cap = cv2.VideoCapture(source)

    def generate():
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow('frame', frame)
            if cv2.waitKey(1) == ord('q'):
                break

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                break
            frame = buffer.tobytes()
            data = (b'--frame\r\n'
                    b'Content-Type:image/jpeg\r\n'
                    b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'
                    b'\r\n' + frame + b'\r\n')

            yield data

    httpx.post(f'https://strm.ftp.sh/{args.stream}', data=generate())

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
