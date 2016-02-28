import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
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
    return requests.get(list_contacts, headers=headers).text

ns = {
        'feed': 'http://www.w3.org/2005/Atom',
        'gd': 'http://schemas.google.com/g/2005',
}

class Contact(object):
    def __init__(self, node):
        self.node = node
    
    def update(self):
        # TODO: Finish out this update method.
        # needs:
        # - properties need to affect the underlying XML model.
        # - headers need to include the If-Match.
        headers = {
        'authorization': 'Bearer ' + auth_token,
        'Content-Type': 'application/atom+xml',
        'GData-Version': '3.0',
        'If-Match': '{0.etag}'.format(self),
        }
        print('headers: {}'.format(headers))
        payload = ET.tostring(self.node)
        url = "https://www.google.com/m8/feeds/contacts/default/full/{}".format(self.contact_id)
        requests.put(url=url, headers=headers, data=payload)

    @property
    def contact_id(self):
        id_element = self.node.find('feed:id', ns)
        return id_element.text.split('/')[-1]
    
    def __str__(self):
        return "<Contact Names: {} : Emails: {} : ID: {} >".format(self.names, self.emails, self.contact_id)

    @property
    def etag(self):
        # attrib gets don't honor the namespace lookups with ns... :(
        return self.node.attrib.get('{http://schemas.google.com/g/2005}etag')

    @property
    def emails(self):
        return [x.attrib.get('address') for x in self.node.findall('gd:email', ns)]

    def clean_emails(self):
        """
        This was the method I used to sanitize my wife's emails.  Basically, it boiled down
        to removing the 'e' and 'i' in front of the '@' in the emails.  (We really weren't 
        that concerned with accidentally hitting one that was legimitely i or e in front of @,
        because those seemed to have an extra 'i' or 'e', and it seemed that they were *all* 
        affected...)

        I'll be removing this in a future release when I turn this into more of an API,
        but wanted to include it here for the curious for now, and until I give a Python
        DFW Pythoneers presentation on this.

        Is this bad OO design?  Yup!  Did it work?  Yup!  :-)
        """
        emails = self.node.findall('gd:email', ns)
        for e in emails:
            addy = e.attrib.get('address')
            if 'i@' in addy:
                replaced = True
                print('before replacement {}'.format(addy))
                e.attrib['address'] = addy.replace('i@', '@')
                print('after replacement {}'.format(e.attrib.get('address')))
            elif 'e@' in addy:
                replaced = True
                print('before replacement {}'.format(addy))
                e.attrib['address'] = addy.replace('e@', '@')
                print('after replacement {}'.format(e.attrib.get('address')))
            else:
                print('not modified {}'.format(e.attrib.get('address')))

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


def parse_contact_list():
    try:
        root = ET.fromstring(get_contact_list())
    except ET.ParseError:
        raise Exception("Could not parse XML Contact List.  Did you forget to update your config Oauth2 key?")
    cl = ContactList(root)
    for c in cl:
        print(c)    

if __name__ == "__main__":
    parse_contact_list()