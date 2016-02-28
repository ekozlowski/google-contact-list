import requests
import xml.etree.ElementTree as ET
import config

auth_token = config.auth_token

def get_contact_list():
    headers = {
        'authorization': 'Bearer ' + auth_token,
        'Host': 'www.google.com',
        'Gdata-version': '3.0',
        'content-length': '0',
    }
    list_contacts = "https://www.google.com/m8/feeds/contacts/default/full?max-results=2000"
    open('./contact_list.xml', 'w').write(requests.get(list_contacts, headers=headers).text)

ns = {
        'feed': 'http://www.w3.org/2005/Atom',
        'gd': 'http://schemas.google.com/g/2005',
}
    
class Contact(object):
    def __init__(self, node):
        self.node = node
        
    def __str__(self):
        return "<Contact Names: {} : Emails: {}>".format(self.names, self.emails)

    @property
    def contact_id(self):
        self.node.attrib.get('gd:etag')

    @property
    def emails(self):
        return [x.attrib.get('address') for x in self.node.findall('gd:email', ns)]

    @property
    def names(self):
        r = []
        names = self.node.findall('gd:name', ns)
        for n in names:
            fn = n.find('gd:fullName', ns)
            r.append(fn.text)
        return r

class ContactList(object):
    def __init__(self, node):
        self.node = node
        self.contacts = [Contact(c) for c in self.node.findall('feed:entry', ns)]
        print("I have {} contacts loaded.".format(len(self.contacts)))

    def __iter__(self):
        return iter(self.contacts)

    def getContactsWithBadEmails(self):
        contacts_with_emails = [c for c in self.contacts if c.emails]
        print("There are {} contacts with email addresses.".format(len(contacts_with_emails)))

def parse_contact_list():
    tree = ET.parse('./contact_list.xml')
    root = tree.getroot()
    cl = ContactList(root)

if __name__ == "__main__":
    get_contact_list()
    parse_contact_list()