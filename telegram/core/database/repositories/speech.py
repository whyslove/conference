from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import select, delete
from typing import Optional, List, Union
from uuid import uuid4 as create_uuid
from datetime import datetime

from create_table import Speech


class SpeechRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, key: Optional[str] = '', title='',
                      start_time: Optional[datetime] = '', end_time: Optional[datetime] = '',
                      venue='', venue_description='') -> List[Optional[dict]]:
        """The function of getting all speeches from the Speech table.

        :param key: unique code of speech (replace None with new uuid)
        :type key: str | None

        :param title: topic of speech
        :type title: str

        :param start_time: start time of speech
        :type start_time: datetime

        :param end_time: end time of speech
        :type end_time: datetime

        :param venue: venue for the speaker
        :type venue: str

        :param venue_description: description of venue
        :type venue_description: str

        :return: list of dictionaries - json format of the requested object
        :rtype: List[dict | None]

        """

        query = select(Speech)

        if key != '' and key is not None:
            query = query.where(Speech.key == key)

        if title != '':
            query = query.where(Speech.title == title)

        if start_time != '':
            query = query.where(Speech.start_time == start_time)

        if end_time != '':
            query = query.where(Speech.end_time == end_time)

        if venue != '':
            query = query.where(Speech.venue == venue)

        if venue_description != '':
            query = query.where(Speech.venue_description == venue_description)

        speeches = [
            {
                'key': speech.key,
                'title': speech.title,
                'start_time': speech.start_time,
                'end_time': speech.end_time,
                'venue': speech.venue,
                'venue_description': speech.venue_description
            } for speech in (await self.session.execute(query)).scalars()
        ]

        return speeches

    async def get_one(self, key: Optional[str] = '', title='',
                      start_time: Optional[datetime] = '', end_time: Optional[datetime] = '',
                      venue='', venue_description='') -> Optional[dict]:
        """The function of getting one speech from the Speech table.

        :param key: unique code of speech (replace None with new uuid)
        :type key: str | None

        :param title: topic of speech
        :type title: str

        :param start_time: start time of speech
        :type start_time: datetime

        :param end_time: end time of speech
        :type end_time: datetime

        :param venue: venue for the speaker
        :type venue: str

        :param venue_description: description of venue
        :type venue_description: str

        :return: dictionary - json format of the requested object; or nothing
        :rtype: dict | None

        """

        speeches = await self.get_all(
            key=key,
            title=title,
            start_time=start_time,
            end_time=end_time,
            venue=venue,
            venue_description=venue_description
        )

        if speeches and speeches[0]:
            return speeches[0]
        return None

    async def delete(self, key='', title='',
                     start_time: Optional[datetime] = '', end_time: Optional[datetime] = '',
                     venue='', venue_description='') -> None:
        """The function of deleting speeches from the Speech table.

        :param key: unique code of speech
        :type key: str

        :param title: topic of speech
        :type title: str

        :param start_time: start time of speech
        :type start_time: datetime

        :param end_time: end time of speech
        :type end_time: datetime

        :param venue: venue for the speaker
        :type venue: str

        :param venue_description: description of venue
        :type venue_description: str

        :return: nothing
        :rtype: None

        """

        query = delete(Speech)

        if key != '':
            query = query.where(Speech.key == key)

        if title != '':
            query = query.where(Speech.title == title)

        if start_time != '':
            query = query.where(Speech.start_time == start_time)

        if end_time != '':
            query = query.where(Speech.end_time == end_time)

        if venue != '':
            query = query.where(Speech.venue == venue)

        if venue_description != '':
            query = query.where(Speech.venue_description == venue_description)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(self, speeches: Union[dict, List[dict]]) -> Union[dict, List[dict]]:
        """The function of adding speeches to the Speech table.

        :param speeches: dictionary or list of dictionaries - json format of the received objects
        :type speeches: dict | List[dict]

        :return: dictionary or list of dictionaries - json format of the received objects
        :rtype: dict | List[dict]

        """

        query = select(Speech).distinct()
        keys = {speech.key for speech in (await self.session.execute(query)).scalars()}

        if type(speeches) == dict:
            speeches = [speeches]

        return_speeches = []

        for speech in speeches:
            params = {}

            if 'key' in speech.keys() and speech['key'] is not None:
                if speech['key'] in keys:
                    raise ValueError(f'Unable to add new speech with parameter '
                                     f'key="{speech["key"]}" '
                                     f'because this key already exists.')
                params['key'] = speech['key']
            else:
                params['key'] = str(create_uuid())

            if 'title' in speech.keys():
                params['title'] = speech['title']
            else:
                raise ValueError(f'Unable to add new speech '
                                 f'because a parameter "title" does not exist.')

            if 'start_time' in speech.keys():
                params['start_time'] = speech['start_time']
            else:
                raise ValueError(f'Unable to add new speech '
                                 f'because a parameter "start_time" does not exist.')

            if 'end_time' in speech.keys():
                params['end_time'] = speech['end_time']
            else:
                raise ValueError(f'Unable to add new speech '
                                 f'because a parameter "end_time" does not exist.')

            if 'venue' in speech.keys():
                params['venue'] = speech['venue']
            else:
                raise ValueError(f'Unable to add new speech '
                                 f'because a parameter "venue" does not exist.')

            if 'venue_description' in speech.keys():
                params['venue_description'] = speech['venue_description']
            else:
                raise ValueError(f'Unable to add new speech '
                                 f'because a parameter "venue_description" does not exist.')

            self.session.add(Speech(**params))
            keys.add(params['key'])

            await self.session.commit()
            return_speeches.append(params)

        if len(return_speeches) == 1:
            return_speeches = return_speeches[0]

        return return_speeches

    async def update(self, key='', title='',
                     start_time: Optional[datetime] = '', end_time: Optional[datetime] = '',
                     venue='', venue_description='', new_key='', new_title='',
                     new_start_time: Optional[datetime] = '', new_end_time: Optional[datetime] = '',
                     new_venue='', new_venue_description='') -> None:
        """The function of updating speeches in the Speech table.

        :param key: unique code of speech
        :type key: str

        :param title: topic of speech
        :type title: str

        :param start_time: start time of speech
        :type start_time: datetime

        :param end_time: end time of speech
        :type end_time: datetime

        :param venue: venue for the speaker
        :type venue: str

        :param venue_description: description of venue
        :type venue_description: str

        :param new_key: new unique code of speech
        :type new_key: str

        :param new_title: new topic of speech
        :type new_title: str

        :param new_start_time: new start time of speech
        :type new_start_time: datetime

        :param new_end_time: new end time of speech
        :type new_end_time: datetime

        :param new_venue: new venue for the speaker
        :type new_venue: str

        :param new_venue_description: new description of venue
        :type new_venue_description: str

        :return: nothing
        :rtype: None

        """

        params = dict()
        query = select(Speech)

        if key != '':
            params['key'] = key
            query = query.where(Speech.key == key)

        if title != '':
            params['title'] = title
            query = query.where(Speech.title == title)

        if start_time != '':
            params['start_time'] = start_time
            query = query.where(Speech.start_time == start_time)

        if end_time != '':
            params['end_time'] = end_time
            query = query.where(Speech.end_time == end_time)

        if venue != '':
            params['venue'] = venue
            query = query.where(Speech.venue == venue)

        if venue_description != '':
            params['venue_description'] = venue_description
            query = query.where(Speech.venue_description == venue_description)

        if not params:
            return

        speeches = (await self.session.execute(query)).scalars()

        query = select(Speech).distinct()
        keys = {speech.key for speech in (await self.session.execute(query)).scalars()}

        for speech in speeches:
            if new_key != '':
                if new_key not in keys:
                    keys.remove(speech.key)
                    speech.key = new_key
                    keys.add(new_key)
                else:
                    ValueError(f'Unable to update the value in speech '
                               f'because speech with this '
                               f'key="{new_key}" already exists.')

            if new_title != '':
                speech.title = new_title

            if new_start_time != '':
                speech.start_time = new_start_time

            if new_end_time != '':
                speech.end_time = new_end_time

            if new_venue != '':
                speech.venue = new_venue

            if new_venue_description != '':
                speech.venue_description = new_venue_description

            await self.session.commit()
