from mailbox import Message


def main():
    message = Message()
    message['From'] = 'test@example.com'
    message['To'] = 'test2@example.com'
    message['Subject'] = 'Test'
    message.set_payload('Test')
    print(message)

if __name__ == "__main__":
    main()