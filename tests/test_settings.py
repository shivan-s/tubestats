#!usr/bin/env python3
# test/test_setting.py - contains settings such as test channel cases
#
# by Shivan Sivakumaran

def set_channel_ID_test_case() -> str:
    """
    Sets channel test ID

    :params: None
    :return: channel ID
    :rtype: str
    """
    # set this to desired channel
    CHANNEL = 'jeffstar'

    test_channels = { 
            'ali': 'UCoOae5nYA7VqaXzerajD0lg',          # Ali Abdaal
            'jeffstar': 'UCkvK_5omS-42Ovgah8KRKtg',     # Jeffery Star
            'shiv': 'UCrbYXWUmeCy4GqArthu4hCw',         # Shivan Sivakumaran (me)
            'dbourke': 'UCr8O8l5cCX85Oem1d18EezQ',      # Daniel Bourke
            }

    channel_ID = test_channels[CHANNEL]
    return channel_ID

def main():
    return

if __name__ == '__main__':
    main()
