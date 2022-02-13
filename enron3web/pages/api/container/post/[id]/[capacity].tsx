import { collection, doc, getDocs, query, setDoc, where } from "firebase/firestore";
import { db, initFirebase } from "../../../../../lib/initFirebase";

export default async function handler(req: any, res: any) {
    const { id, capacity } = req.query

    if (req.method != "POST") res.end(500);


    try {
      initFirebase();

      const q = query(collection(db, "container"), where("id", "==", `${id}`));

      const querySnapshot = await getDocs(q);
      let containerList = querySnapshot.docs.map((doc) => 
          doc.data()
      );

      const containerRef = collection(db, "container");
      const docRef = doc(containerRef, `${id}`)

      containerList[0].capacity=capacity

      await setDoc(docRef,containerList[0])
      res.status(200);
      res.end(`Post:${id} - ${capacity}`)

  } catch (error) {
      console.log(error)
      res.status(500);
  }
  }
