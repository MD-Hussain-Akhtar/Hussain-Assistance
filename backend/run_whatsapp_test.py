from whatsapp_v2 import WhatsAppMessenger

if __name__ == '__main__':
    wa = WhatsAppMessenger()
    print("Starting WhatsApp quick-message test -> recipient: 'papa', text: 'hello'")
    result = wa.quick_message('papa', 'hello')
    print('Result:', result)
