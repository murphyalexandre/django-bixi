from xml.etree import ElementTree
from datetime import datetime
import urllib2

from django.core.management.base import BaseCommand, CommandError

from bixi.models import City, Station, Update


class Command(BaseCommand):
    args = '<city_code city_code ...>'
    help = 'Updates the current bike and dock counts for a given list of cities.'

    @staticmethod
    def timestampToDateTime(timestamp):
        if timestamp:
            return datetime.fromtimestamp(int(timestamp) / 1e3)
        return None

    def handle(self, *args, **options):
        city_codes = args or \
            map(lambda x: x[0], City.available.all().values_list('code'))

        for city_code in city_codes:
            try:
                city = City.objects.get(code=city_code)
            except City.DoesNotExist:
                raise CommandError('City "%s" does not exist.' % city_code)

            xml = urllib2.urlopen(city.url)
            tree = ElementTree.parse(xml)
            root = tree.getroot()

            created = 0
            updated = 0
            statusquo = 0

            stations = root.findall('station')
            for s in stations:
                public_id = int(s.find('id').text)
                if s.find('lastCommWithServer') is not None:
                    last_comm_with_server = Command.timestampToDateTime(
                        s.find('lastCommWithServer').text)
                else:
                    last_comm_with_server = None
                try:
                    station = Station.objects.get(
                        city=city, public_id=public_id)
                    if station.last_comm_with_server == last_comm_with_server:
                        statusquo = statusquo + 1
                        self.progress('.')
                        continue
                    else:
                        updated = updated + 1
                        self.progress('u')
                except Station.DoesNotExist:
                    name = s.find('name').text
                    terminal_name = s.find('terminalName').text
                    station = Station()
                    station.city = city
                    station.public_id = public_id
                    station.name = name
                    station.terminal_name = terminal_name
                    created = created + 1
                    self.progress('c')
                latitude = float(s.find('lat').text)
                longitude = float(s.find('long').text)
                installed = s.find('installed').text == 'true'
                locked = s.find('locked').text == 'true'
                install_date = Command.timestampToDateTime(
                    s.find('installDate').text)
                removal_date = Command.timestampToDateTime(
                    s.find('removalDate').text)
                temporary = s.find('temporary').text == 'true'
                if s.find('public') is not None:
                    public = s.find('public').text == 'true'
                else:
                    public = None
                nb_bikes = int(s.find('nbBikes').text)
                nb_empty_docks = int(s.find('nbEmptyDocks').text)
                if s.find('latestUpdateTime') is not None:
                    latest_update_time = Command.timestampToDateTime(
                        s.find('latestUpdateTime').text)
                else:
                    latest_update_time = datetime.now()
                station.last_comm_with_server = last_comm_with_server
                station.latitude = latitude
                station.longitude = longitude
                station.installed = installed
                station.locked = locked
                station.install_date = install_date
                station.removal_date = removal_date
                station.temporary = temporary
                station.public = public
                station.save()

                if Update.objects.filter(station=station,
                    latest_update_time=latest_update_time).exists():
                    continue

                Update.objects.create(station=station, nb_bikes=nb_bikes,
                    nb_empty_docks=nb_empty_docks,
                    latest_update_time=latest_update_time)

            last_update = Command.timestampToDateTime(root.attrib['lastUpdate'])
            city.last_update = last_update
            city.save()

            self.stdout.write('\nSuccessfully updated bike and dock counts for ' +
                '%s.' % city.name)
            self.stdout.write('Created: %s' % created)
            self.stdout.write('Updated: %s' % updated)
            self.stdout.write('Status quo: %s' % statusquo)

    def progress(self, str):
        self.stdout.write(str, ending='')
