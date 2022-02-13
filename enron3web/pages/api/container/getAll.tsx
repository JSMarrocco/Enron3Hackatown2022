import { query, collection, getDocs, DocumentData } from "firebase/firestore";
import { db, initFirebase } from "../../../lib/initFirebase";

export default async function handler(req: any, res: any) {
    if (req.method != "GET") res.status(500);

    try {
        initFirebase();

        const q = query(collection(db, "container"));

        const querySnapshot = await getDocs(q);
        let containerList = querySnapshot.docs.map((doc) => 
            doc.data()
        );
        res.status(200).json(containerList)

                  
    } catch (error) {
        console.log(error)
        res.status(500);

    }

  }